"""Shared environment policy for the docs sample sweep.

Every runner verifies the code samples of one site section against the
installed `kaappi` binary. This module centralizes the few things that
differ between a developer laptop and CI:

- KAAPPI_WS       root of the multi-repo workspace (optional). When set,
                  uninstalled pure-Scheme ecosystem libraries and the core
                  repo's lib/ tree resolve from here.
- SWEEP_WORK      scratch directory for generated programs and fixtures
                  (default: a per-run directory under the system tempdir).
- SWEEP_PG_USE_EXISTING=1
                  use an already-existing scratch PostgreSQL database
                  (CI service container). Without it, runners only touch a
                  database they create themselves and drop afterwards.
"""
import os, pathlib, shutil, socket, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
WS = os.environ.get("KAAPPI_WS")
IS_DARWIN = sys.platform == "darwin"
LIBM = "libm.dylib" if IS_DARWIN else "libm.so.6"
DYLIB_EXT = "dylib" if IS_DARWIN else "so"

_work = os.environ.get("SWEEP_WORK")
WORK = pathlib.Path(_work) if _work else \
    pathlib.Path(tempfile.gettempdir()) / "kaappi-docs-sweep"
WORK.mkdir(parents=True, exist_ok=True)


def work(section):
    d = WORK / section
    d.mkdir(parents=True, exist_ok=True)
    return d


def platformize(src):
    """Doc samples are written macOS-first; translate the shared-library
    names when running elsewhere."""
    if IS_DARWIN:
        return src
    return src.replace("libm.dylib", LIBM)


def ws_lib(repo):
    """--lib-path for a workspace ecosystem repo, when available."""
    if not WS:
        return None
    p = pathlib.Path(WS) / repo / "lib"
    return str(p) if p.exists() else None


def lib_args(*repos):
    out = []
    for r in repos:
        p = ws_lib(r)
        if p:
            out += ["--lib-path", p]
    return out


def importable(libname, extra_args=()):
    """True when (import (<libname>)) succeeds for the installed kaappi."""
    try:
        r = subprocess.run(
            ["kaappi", *extra_args, "/dev/stdin"],
            input=f"(import ({libname}))\n", capture_output=True, text=True,
            timeout=300)
    except subprocess.TimeoutExpired:
        return False
    return r.returncode == 0


def core_lib_args():
    """(kaappi parallel) ships in the core repo's lib/ tree but was missing
    from release tarballs up to v0.21.0 (fixed on core main by kaappi#1759).
    Probe the install first so this self-activates once a fixed release
    ships; fall back to the workspace core repo meanwhile."""
    if importable("kaappi parallel"):
        return []
    if WS:
        p = pathlib.Path(WS) / "kaappi" / "lib"
        if p.exists() and importable("kaappi parallel",
                                     ["--lib-path", str(p)]):
            return ["--lib-path", str(p)]
    return None      # unavailable — callers skip parallel content


def have_ffi():
    """Released Linux binaries up to v0.21.0 lack dynamic loading, which
    disables the whole C-FFI ecosystem there (fixed on core main by
    kaappi#1783; the next release activates these checks). Detect it once
    so FFI-dependent checks skip instead of failing."""
    r = subprocess.run(
        ["kaappi", "/dev/stdin"],
        input=f'(import (kaappi ffi))\n(ffi-open "{LIBM}")\n',
        capture_output=True, text=True, timeout=60)
    return r.returncode == 0


HAVE_FFI = have_ffi()
if not HAVE_FFI:
    print("NOTE: this kaappi build has no dynamic loading — "
          "FFI-dependent checks are skipped", file=sys.stderr)


def port_open(port, host="127.0.0.1"):
    try:
        with socket.create_connection((host, port), 0.5):
            return True
    except OSError:
        return False


def install_workspace_dylibs(*names):
    """Copy workspace-built C-extension dylibs into ~/.kaappi/lib so
    ffi-open's bare-name lookup finds them. Returns paths we created (the
    caller removes them); pre-existing installs are left alone."""
    created = []
    home_lib = pathlib.Path.home() / ".kaappi" / "lib"
    if not WS:
        return created
    for name in names:
        src = pathlib.Path(WS) / f"kaappi-{name}" / f"libkaappi_{name}.{DYLIB_EXT}"
        tgt = home_lib / src.name
        if src.exists() and not tgt.exists():
            shutil.copy(src, tgt)
            created.append(tgt)
    return created
