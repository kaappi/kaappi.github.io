// Shared Web Worker runner for the playground and tour.
//
// Owns the worker lifecycle and the client half of the worker protocol
// (request { code, wasmUrl } -> response { stdout, stderr, elapsed }, defined
// in playground-worker.js). A hung program is bounded by a hard timeout that
// terminates the worker and respawns a fresh one for the next run.

const TIMEOUT_MS = 5000;

export function createRunner() {
  const workerUrl = new URL("./playground-worker.js", import.meta.url);
  const wasmUrl = new URL("../wasm/kaappi.wasm", import.meta.url).href;
  let worker = new Worker(workerUrl, { type: "module" });

  function run(code) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        worker.terminate();
        worker = new Worker(workerUrl, { type: "module" });
        reject(new Error(`Timed out (${TIMEOUT_MS / 1000} s limit)`));
      }, TIMEOUT_MS);

      worker.onmessage = ({ data }) => { clearTimeout(timer); resolve(data); };
      worker.onerror = (e) => { clearTimeout(timer); reject(new Error(e.message || "Worker error")); };
      worker.postMessage({ code, wasmUrl });
    });
  }

  return {
    run,
    terminate: () => worker.terminate(),
  };
}
