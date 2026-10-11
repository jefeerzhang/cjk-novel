"""Locate, install and inspect a XeLaTeX engine.

tectonic is preferred: one binary, no TeX Live, reruns itself.
xelatex is the fallback: plenty of machines already have a TeX distribution.
"""
import os
import platform
import shutil
import subprocess
import sys

PREFERRED = "tectonic"
FALLBACK = "xelatex"


def which(name):
    return shutil.which(name)


def pick(prefer_fallback=False):
    """Return (engine, executable path) or (None, None)."""
    order = [FALLBACK, PREFERRED] if prefer_fallback else [PREFERRED, FALLBACK]
    for e in order:
        p = which(e)
        if p:
            return e, p
    return None, None


def version(exe):
    for args in (["--version"], ["-v"], ["--version-only"]):
        try:
            p = subprocess.run([exe] + args, capture_output=True, text=True,
                               timeout=20, encoding="utf-8", errors="replace")
            out = (p.stdout or p.stderr).strip().splitlines()
            if out:
                return out[0].strip()
        except Exception:
            pass
    return "unknown"


def cache_dir():
    sysname = platform.system()
    if sysname == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "TectonicProject", "Tectonic")
    if sysname == "Darwin":
        return os.path.expanduser("~/Library/Caches/Tectonic")
    return os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache/Tectonic")


def cache_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def installers():
    """Ordered (manager, argv, note) tuples for the current platform."""
    sysname = platform.system()
    if sysname == "Windows":
        return [
            ("scoop", ["scoop", "install", PREFERRED], "per-user, no admin"),
            ("choco",  ["choco", "install", PREFERRED, "-y"], "may need an admin shell"),
            ("cargo",  ["cargo", "install", PREFERRED], "if you already have Rust"),
        ]
    if sysname == "Darwin":
        return [
            ("brew",  ["brew", "install", "tectonic"], ""),
            ("cargo", ["cargo", "install", PREFERRED], "if you already have Rust"),
        ]
    mgr, argv = None, None
    for m, a in (("apt-get", ["apt-get", "install", "-y", "tectonic"]),
                 ("dnf", ["dnf", "install", "-y", "tectonic"]),
                 ("pacman", ["pacman", "-S", "--noconfirm", "tectonic"])):
        if which(m):
            mgr, argv = m, a
            break
    out = []
    if mgr:
        out.append((mgr, argv, "may need sudo"))
    out.append(("cargo", ["cargo", "install", PREFERRED], "if you already have Rust"))
    return out


def available_installers():
    return [(m, a, n) for m, a, n in installers() if which(m)]


def install(progress=print):
    """Install tectonic using the first package manager found.

    Returns True on success. This only runs when the caller explicitly asks.
    """
    cands = available_installers()
    if not cands:
        return False
    for mgr, argv, _note in cands:
        progress("installing tectonic with %s ..." % mgr)
        try:
            p = subprocess.run(argv)
        except Exception as exc:                       # noqa: BLE001
            progress("  %s failed: %s" % (mgr, exc))
            continue
        if p.returncode == 0 and which(PREFERRED):
            return True
        progress("  %s exited %s" % (mgr, p.returncode))
    return False
