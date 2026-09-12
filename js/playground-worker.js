// Web Worker that runs Scheme in the WASM interpreter for the playground and tour.
//
// Two execution paths, picked by feature-detecting the WASM's exports:
//
//   Stepped (preferred) — when the binary exports the bounded-step entry point
//   (kaappi#2283: kaappi_step_alloc/setup/run/stop/reset), pump it in a loop:
//   run a chunk of bytecode, hand control back to the event loop, repeat. Between
//   chunks we flush streamed stdout/stderr to the page, honor a cooperative Stop,
//   and enforce a generous wall-clock backstop — so a long, constant-space program
//   keeps running and keeps showing output instead of being killed at a hard 5 s.
//
//   Batch (fallback) — an older binary without those exports runs the classic way:
//   a single blocking WASI `_start`. Output still reaches the page, but it can't be
//   streamed or cooperatively stopped mid-run; kp-runner.mjs's hard-kill timeout is
//   the only guard there. This path lets the site deploy against a released WASM
//   that predates the step entry point and upgrade automatically once one ships it.
//
// Protocol (see kp-runner.mjs for the client half):
//   main -> worker : { type: "run", code, wasmUrl } | { type: "stop" }
//   worker -> main : { type: "stdout"|"stderr", chunk }
//                    { type: "done", elapsed, error, stopped, timedOut, mode }

// Bytecode instructions per pump. Bounds Stop/stream latency (one chunk) against
// per-chunk overhead; the exact value isn't load-bearing for correctness.
const STEP_BUDGET = 1_000_000;
// Cooperative wall-clock backstop for a runaway (or infinite) stepped program.
// Far more generous than the old 5 s hard kill, and — unlike it — output produced
// so far is preserved and dynamic-wind after-thunks still run on the way out.
const WALL_CLOCK_MS = 30_000;
// After a stop is requested the VM unwinds over the next step(s); cap how many
// chunks we'll pump waiting for that, so a pathological after-thunk can't wedge
// the worker in an unbounded JS loop.
const POST_STOP_CHUNK_CAP = 2_000;
// Per-stream cap on how much output we forward to the page. A tight print loop
// can emit tens of MB; past this we drop the rest (with a one-time notice) so an
// unbounded string can't wedge the main thread or balloon the DOM. The program
// itself keeps running — this bounds display, not execution.
const MAX_OUTPUT_CHARS = 200_000;

// kaappi_step_run return codes (src/wasm_step.zig).
const RUN_RUNNING = 0;
const RUN_DONE = 1;
const RUN_ERROR = 2;

let wasmModule = null;
let wasiShim = null;

// The instance of the program currently being pumped, so a "stop" message can
// reach its kaappi_step_stop() between chunks. Null except during a stepped run.
let activeInstance = null;
let stopRequested = false;

const yieldToEventLoop = () => new Promise((resolve) => setTimeout(resolve, 0));

// Accumulates one stream's output and flushes it to the page in per-chunk
// batches rather than per line — a fast loop emits far too many lines to post
// one message each. Enforces MAX_OUTPUT_CHARS, emitting a truncation notice once.
function makeSink(type) {
  let pending = "";
  let sent = 0;
  let truncated = false;
  let sawAny = false;
  return {
    push(text) {
      sawAny = true;
      if (!truncated) pending += text;
    },
    flush() {
      if (!pending) return;
      let out = pending;
      pending = "";
      if (sent + out.length >= MAX_OUTPUT_CHARS) {
        out = out.slice(0, Math.max(0, MAX_OUTPUT_CHARS - sent));
        truncated = true;
      }
      if (out) {
        self.postMessage({ type, chunk: out });
        sent += out.length;
      }
      if (truncated) {
        self.postMessage({ type, chunk: `\n[output truncated at ${MAX_OUTPUT_CHARS} characters]\n` });
      }
    },
    get sawAny() { return sawAny; },
  };
}

self.onmessage = ({ data }) => {
  if (data.type === "stop") {
    stopRequested = true;
    if (activeInstance) {
      try { activeInstance.exports.kaappi_step_stop(); } catch { /* torn down already */ }
    }
    return;
  }
  if (data.type === "run") {
    run(data.code, data.wasmUrl);
  }
};

async function run(code, wasmUrl) {
  stopRequested = false;
  try {
    if (!wasiShim) wasiShim = await import("./wasi-shim-bundle.mjs");
    if (!wasmModule) {
      const response = await fetch(wasmUrl);
      if (!response.ok) throw new Error(`Failed to fetch WASM: ${response.status}`);
      wasmModule = await WebAssembly.compile(await response.arrayBuffer());
    }

    const { WASI, File, OpenFile, ConsoleStdout, PreopenDirectory } = wasiShim;

    // Collect output line by line into batched sinks. fd 1/2 are unbuffered in
    // the runtime, so lines land as the program runs (stepped) and each chunk's
    // sink.flush() surfaces them. `\n` per line reproduces the batch output
    // (join("\n") + trailing "\n"); a final unterminated line isn't flushed —
    // the same limitation the batch path has always had.
    const stdout = makeSink("stdout");
    const stderr = makeSink("stderr");
    const fds = [
      new OpenFile(new File([])),
      ConsoleStdout.lineBuffered((line) => stdout.push(line + "\n")),
      ConsoleStdout.lineBuffered((line) => stderr.push(line + "\n")),
      new PreopenDirectory(".", [
        ["program.scm", new File(new TextEncoder().encode(code))],
      ]),
    ];

    // debug:false — the bundled shim otherwise logs every WASI call to console.
    const wasi = new WASI(["kaappi", "program.scm"], [], fds, { debug: false });
    const instance = await WebAssembly.instantiate(wasmModule, {
      wasi_snapshot_preview1: wasi.wasiImport,
    });

    if (typeof instance.exports.kaappi_step_run === "function") {
      await runStepped(instance, wasi, code, stdout, stderr);
    } else {
      runBatch(instance, wasi, stdout, stderr);
    }
  } catch (e) {
    self.postMessage({ type: "stderr", chunk: String(e && e.message ? e.message : e) });
    self.postMessage({ type: "done", elapsed: 0, error: true, stopped: false, timedOut: false, mode: "error" });
  }
}

// Pump the bounded-step entry point: run a chunk, flush streamed output, yield,
// check the Stop flag and the wall-clock backstop, repeat until it finishes.
async function runStepped(instance, wasi, code, stdout, stderr) {
  const ex = instance.exports;
  wasi.initialize(instance); // wire wasi.inst for fd_write; does NOT run _start

  const src = new TextEncoder().encode(code);
  const ptr = ex.kaappi_step_alloc(src.length);
  if (!ptr) throw new Error("Out of memory");
  // Fetch memory.buffer after alloc — growing linear memory detaches any view.
  new Uint8Array(ex.memory.buffer, ptr, src.length).set(src);
  const setup = ex.kaappi_step_setup(ptr, src.length);
  if (setup !== 0) throw new Error(`Interpreter setup failed (code ${setup})`);

  activeInstance = instance;
  const t0 = performance.now();
  let status = RUN_RUNNING;
  let timedOut = false;
  let postStopChunks = 0;
  try {
    while (true) {
      status = ex.kaappi_step_run(STEP_BUDGET);
      stdout.flush();
      stderr.flush();
      if (status !== RUN_RUNNING) break;

      await yieldToEventLoop(); // let a queued "stop" message be delivered

      const overBudget = performance.now() - t0 > WALL_CLOCK_MS;
      if (stopRequested || overBudget) {
        if (overBudget) timedOut = true;
        ex.kaappi_step_stop(); // idempotent; VM unwinds and returns RUN_DONE soon
        if (++postStopChunks > POST_STOP_CHUNK_CAP) { status = RUN_DONE; break; }
      }
    }
  } finally {
    activeInstance = null;
    try { ex.kaappi_step_reset(); } catch { /* instance is discarded regardless */ }
  }

  const elapsed = performance.now() - t0;
  self.postMessage({
    type: "done",
    elapsed,
    error: status === RUN_ERROR || stderr.sawAny,
    stopped: stopRequested,
    timedOut,
    mode: "stepped",
  });
}

// Classic single-shot path for a WASM without the step entry point. Blocks the
// worker until the program returns, so a "stop" can't be observed here — the
// client's hard-kill timeout is the guard.
function runBatch(instance, wasi, stdout, stderr) {
  const t0 = performance.now();
  try {
    wasi.start(instance);
  } catch (e) {
    // A trap, or a non-zero proc_exit surfaced by the shim as { code }.
    if (e instanceof WebAssembly.RuntimeError || (e && e.code !== 0)) {
      stderr.push((e.message ?? String(e)) + "\n");
    }
  }
  stdout.flush();
  stderr.flush();
  const elapsed = performance.now() - t0;
  self.postMessage({
    type: "done",
    elapsed,
    error: stderr.sawAny,
    stopped: false,
    timedOut: false,
    mode: "batch",
  });
}
