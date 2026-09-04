// Shared Web Worker runner for the playground and tour.
//
// Owns the worker lifecycle and the client half of the worker protocol (see
// playground-worker.js). `run` streams stdout/stderr to the caller as the
// program produces it and resolves when it finishes; `stop` asks the running
// program to stop cooperatively.
//
//   run(code, { onStdout, onStderr }) -> Promise<{
//       elapsed, error, stopped, timedOut, mode }>
//   stop()       -> request the running program to stop
//   terminate()  -> tear the worker down (page teardown)
//
// A cooperative stop (the stepped path) unwinds cleanly and keeps output already
// produced. Two hard-kill timers back that up for the cases cooperation can't
// cover — a program without the step entry point (batch path blocks the worker,
// so a Stop can't be observed) or a wedged worker: they terminate and respawn it.

// Backstop for a run that never reports back — e.g. a long batch program on a
// WASM without the step entry point, which blocks the worker until it returns.
// Comfortably above the worker's own 30 s stepped wall-clock budget, so it only
// fires when cooperation isn't possible.
const HARD_KILL_MS = 45_000;
// After a Stop is requested, how long to wait for a cooperative finish before
// hard-killing. The stepped path answers within ~one chunk; the batch path never
// will, so this is what actually stops it.
const STOP_GRACE_MS = 2_000;

export function createRunner() {
  const workerUrl = new URL("./playground-worker.js", import.meta.url);
  const wasmUrl = new URL("../wasm/kaappi.wasm", import.meta.url).href;
  let worker = spawn();

  // The in-flight run, or null when idle.
  let active = null;

  function spawn() {
    const w = new Worker(workerUrl, { type: "module" });
    w.onmessage = onMessage;
    w.onerror = onWorkerError;
    return w;
  }

  function respawn() {
    worker.terminate();
    worker = spawn();
  }

  function clearTimers() {
    if (!active) return;
    clearTimeout(active.hardKillTimer);
    clearTimeout(active.graceTimer);
  }

  function settle(result) {
    if (!active) return;
    const { resolve } = active;
    clearTimers();
    active = null;
    resolve(result);
  }

  function onMessage({ data }) {
    if (!active) return;
    switch (data.type) {
      case "stdout": active.onStdout?.(data.chunk); break;
      case "stderr": active.onStderr?.(data.chunk); break;
      case "done":
        settle({
          elapsed: data.elapsed,
          error: !!data.error,
          stopped: !!data.stopped,
          timedOut: !!data.timedOut,
          mode: data.mode,
        });
        break;
    }
  }

  function onWorkerError(e) {
    if (!active) return;
    active.onStderr?.((e.message || "Worker error") + "\n");
    respawn(); // the worker may be in an unknown state; start clean
    settle({ elapsed: performance.now() - active.startedAt, error: true, stopped: false, timedOut: false, mode: "error" });
  }

  // Terminate and respawn the worker, resolving the in-flight run as the given
  // outcome. Used when cooperation isn't available (batch path) or times out.
  function hardKill(outcome) {
    if (!active) return;
    const { resolve, startedAt } = active;
    clearTimers();
    active = null;
    respawn();
    resolve({ elapsed: performance.now() - startedAt, error: false, mode: "killed", stopped: false, timedOut: false, ...outcome });
  }

  function run(code, { onStdout, onStderr } = {}) {
    // Callers guard against this with their own running flag; resolve rather
    // than reject so an errant double-run can't leave a dangling rejection.
    if (active) return Promise.resolve({ elapsed: 0, error: true, stopped: false, timedOut: false, mode: "busy" });
    return new Promise((resolve) => {
      active = {
        resolve,
        onStdout,
        onStderr,
        startedAt: performance.now(),
        hardKillTimer: setTimeout(() => hardKill({ timedOut: true }), HARD_KILL_MS),
        graceTimer: null,
      };
      worker.postMessage({ type: "run", code, wasmUrl });
    });
  }

  function stop() {
    if (!active) return;
    worker.postMessage({ type: "stop" });
    clearTimeout(active.graceTimer);
    active.graceTimer = setTimeout(() => hardKill({ stopped: true }), STOP_GRACE_MS);
  }

  return {
    run,
    stop,
    terminate: () => worker.terminate(),
  };
}
