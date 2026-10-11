#!/usr/bin/env python3
"""Compile a CJK novel to a 5 x 8 inch PDF.

    python build.py doctor            report on the environment
    python build.py --install         install tectonic (only when you ask it to)
    python build.py --init my-book    scaffold a new book project
    python build.py novel.tex         compile
    python build.py --xelatex novel.tex   force the xelatex fallback
    python build.py --offline novel.tex    fail instead of hitting the network
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

NO_ENGINE = """No XeLaTeX engine found.

Install one with:

{how}

Or let this script do it:   python build.py --install
"""

NET_HINTS = (
    ("connection", "network"),
    ("timed out", "network"),
    ("dns", "network"),
    ("failed to fetch", "network"),
    ("error sending request", "network"),
    ("proxy", "network"),
)


def install_how():
    cands = engine.available_installers()
    if cands:
        return "\n".join("    %-9s %-46s # %s" % (m, " ".join(a), n) for m, a, n in cands)
    lines = ["    %-9s %-46s # %s" % (m, " ".join(a), n) for m, a, n in engine.installers()]
    lines.append("\n    (none of those package managers are installed on this machine)")
    return "\n".join(lines)


def doctor():
    ok = True
    print("cjk-novel environment\n")

    eng, exe = engine.pick()
    if eng:
        print("  engine      ok    %s  (%s)" % (eng, engine.version(exe)))
    else:
        ok = False
        print("  engine      MISSING  neither tectonic nor xelatex is on PATH")
        print("\n  install one with:\n%s" % install_how())
        print("\n    or: python build.py --install")

    if eng == engine.PREFERRED or which_any(engine.PREFERRED):
        cdir = engine.cache_dir()
        size = engine.cache_size(cdir) if os.path.isdir(cdir) else 0
        if size:
            print("  bundle      ok    %s  (%.0f MB cached)" % (cdir, size / 1e6))
        else:
            print("  bundle      cold  %s is empty" % cdir)
            print("                     the first compile downloads macros one by one (~44 MB)")

    import tempfile as tf
    probe = os.path.join(tf.gettempdir(), ".cjk-novel-write-test")
    try:
        with open(probe, "w") as fh:
            fh.write("x")
        os.remove(probe)
        print("  tempdir     ok    %s" % tf.gettempdir())
    except Exception as exc:                            # noqa: BLE001
        ok = False
        print("  tempdir     FAIL  %s" % exc)

    for label, f in (("body font", "SourceHanSerifCN-Regular.otf"),
                     ("head font", "SourceHanSansCN-Medium.otf")):
        if os.path.isfile(os.path.join(ASSETS, "fonts", f)):
            print("  %-11s ok    assets/fonts/%s" % (label, f))
        else:
            ok = False
            print("  %-11s MISSING  assets/fonts/%s" % (label, f))

    print("\n%s" % ("ready" if ok else "not ready yet"))
    return 0 if ok else 1


def which_any(name):
    return engine.which(name)


def do_init(target):
    target = os.path.abspath(target)
    os.makedirs(os.path.join(target, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(target, "assets"), exist_ok=True)
    shutil.copy2(os.path.join(ASSETS, "novel.tex"), os.path.join(target, "novel.tex"))
    for f in os.listdir(os.path.join(ASSETS, "fonts")):
        dst = os.path.join(target, "fonts", f)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(ASSETS, "fonts", f), dst)
    with open(os.path.join(target, ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write("build/\n*.aux\n*.log\n*.out\n*.toc\n*.synctex.gz\n*.xdv\n")
    print("scaffolded", target)
    print("  write your text in novel.tex, then: python build.py novel.tex")


def find_tex(arg):
    if arg:
        return os.path.abspath(arg)
    for name in ("novel.tex", "main.tex", "book.tex"):
        if os.path.isfile(name):
            return os.path.abspath(name)
    hits = sorted(f for f in os.listdir(".") if f.endswith(".tex"))
    if len(hits) == 1:
        return os.path.abspath(hits[0])
    sys.exit("no .tex file given and none of novel.tex/main.tex found")


def run_engine(eng, exe, tex, proj, outdir, offline):
    stem = os.path.splitext(os.path.basename(tex))[0]
    if eng == engine.PREFERRED:
        cmd = [exe, "-X", "compile", os.path.basename(tex), "--outdir", outdir, "--keep-logs"]
        if offline:
            cmd.append("--only-cached")
        passes = 1          # tectonic reruns itself when cross-references change
    else:
        cmd = [exe, "-interaction=nonstopmode", "-halt-on-error",
               "-output-directory=" + outdir, os.path.basename(tex)]
        passes = 2          # plain xelatex needs a second pass for the page tree
    last = None
    for i in range(passes):
        last = subprocess.run(cmd, cwd=proj, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if last.returncode != 0:
            break
    return last, stem


def diagnose(out, stem, offline):
    low = out.lower()
    for needle, kind in NET_HINTS:
        if needle in low:
            if offline:
                print("\nThe bundle cache is not warm and --offline forbids downloads.")
                print("Drop --offline, or run a build once with network access.")
            else:
                print("\nThis looks like a network failure. tectonic downloads macros on")
                print("demand; the first build needs a working connection. Retry later, or")
                print("point tectonic at a mirror with --bundle <URL>.")
            return True
    if "font" in low and ("not found" in low or "cannot be found" in low):
        print("\nA font is missing. Check that fonts/ holds both Source Han OTF files;")
        print("run `python build.py --init .` in a fresh folder to copy them back.")
        return True
    return False


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("tex", nargs="?")
    ap.add_argument("-o", "--outdir", default="build")
    ap.add_argument("--init", metavar="DIR")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--doctor", action="store_true")
    ap.add_argument("--xelatex", action="store_true", help="force the xelatex fallback")
    ap.add_argument("--offline", action="store_true", help="never hit the network")
    a = ap.parse_args()

    if a.init:
        do_init(a.init)
        return
    if a.doctor or a.tex == "doctor":
        sys.exit(doctor())
    if a.install:
        if engine.pick()[0]:
            print("an engine is already installed:", engine.pick()[0])
            return
        print("about to run:")
        for m, argv, note in engine.available_installers():
            print("  %s   # %s" % (" ".join(argv), note))
        if not engine.install():
            sys.exit("\nnothing worked; install tectonic by hand, then re-run --doctor")
        print("\ntectonic installed:", engine.which(engine.PREFERRED))
        print("next: python build.py doctor")
        return

    eng, exe = engine.pick(prefer_fallback=a.xelatex)
    if not eng:
        sys.exit(NO_ENGINE.format(how=install_how()))

    tex = find_tex(a.tex)
    proj = os.path.dirname(tex)
    os.makedirs(os.path.join(proj, a.outdir), exist_ok=True)
    stem = os.path.splitext(os.path.basename(tex))[0]

    print("engine: %s (%s)" % (eng, engine.version(exe)))
    p, stem = run_engine(eng, exe, tex, proj, a.outdir, a.offline)
    out = (p.stdout or "") + (p.stderr or "")
    sys.stdout.write(out)
    if p.returncode != 0:
        print("\ncompile failed (exit %s)" % p.returncode)
        if not diagnose(out, stem, a.offline):
            print("the log above has the first error; %s.log keeps the full one"
                  % os.path.join(a.outdir, stem))
        sys.exit(1)

    log = os.path.join(proj, a.outdir, stem + ".log")
    pages = "?"
    if os.path.isfile(log):
        m = re.search(r"Output written on .*?\((\d+) pages?",
                      open(log, encoding="utf-8", errors="replace").read())
        if m:
            pages = m.group(1)
    pdf = os.path.join(proj, a.outdir, stem + ".pdf")
    unit = "page" if pages == "1" else "pages"
    print("\nOK  %s %s  ->  %s" % (pages, unit, pdf))
    print("next: python %s %s" % (os.path.join(HERE, "verify.py"), os.path.basename(tex)))


if __name__ == "__main__":
    main()
