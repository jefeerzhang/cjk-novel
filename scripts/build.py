#!/usr/bin/env python3
"""Compile a CJK novel to a 5x8 inch PDF with tectonic.

    python build.py --init my-book      scaffold a new book project
    python build.py novel.tex           compile
    python build.py novel.tex -o out    compile into a different folder
"""
import argparse, os, re, shutil, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, "assets")

INSTALL = """tectonic is not on PATH. Install it with one of:

    scoop install tectonic        # Windows, no admin needed
    choco install tectonic
    cargo install tectonic        # if you already have Rust
    https://tectonic-typesetting.github.io/    # other platforms

First run downloads the TeX bundle (~100 MB) and caches it; later runs are offline.
"""


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
    print("  edit fonts ->", os.path.join(target, "fonts"))
    print("  write your text in novel.tex, then: python build.py novel.tex")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="?")
    ap.add_argument("-o", "--outdir", default="build")
    ap.add_argument("--init", metavar="DIR")
    a = ap.parse_args()

    if a.init:
        do_init(a.init)
        return

    if shutil.which("tectonic") is None:
        sys.exit(INSTALL)

    tex = find_tex(a.tex)
    proj = os.path.dirname(tex)
    stem = os.path.splitext(os.path.basename(tex))[0]
    log = os.path.join(proj, a.outdir, stem + ".log")

    os.makedirs(os.path.join(proj, a.outdir), exist_ok=True)
    cmd = ["tectonic", "-X", "compile", os.path.basename(tex),
           "--outdir", a.outdir, "--keep-logs"]
    p = subprocess.run(cmd, cwd=proj, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    sys.stdout.write(p.stdout or "")
    sys.stderr.write(p.stderr or "")
    if p.returncode != 0:
        sys.exit(f"\ncompile failed (exit {p.returncode})")

    pages = "?"
    if os.path.isfile(log):
        m = re.search(r"Output written on .*?\((\d+) pages?", open(log, encoding="utf-8", errors="replace").read())
        if m:
            pages = m.group(1)
    pdf = os.path.join(proj, a.outdir, stem + ".pdf")
    unit = "page" if pages == "1" else "pages"
    print(f"\nOK  {pages} {unit}  ->  {pdf}")
    print("next: python", os.path.join(SKILL, "scripts", "verify.py"), os.path.basename(tex))


if __name__ == "__main__":
    main()
