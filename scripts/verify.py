#!/usr/bin/env python3
"""Check that a novel project is still on the 5x8in / 22.5pt grid.

    python verify.py novel.tex

Compiles a throwaway probe that asks TeX for the real numbers instead of
guessing from the PDF, so it catches the silent failure mode: someone edits
the font size or setstretch and the baseline grid quietly stops being 22.5pt.
"""
import os, re, shutil, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

EXPECT_LEADING = 22.5   # TeX pt, on the page
EXPECT_SHEET = (5.0, 8.0)
MARK = "PROBE::"


def fail(msgs, ok):
    for m in msgs:
        print(("  ok   " if m.startswith("ok") else "  FAIL ") + m.split("::", 1)[-1].strip())
    print("\n" + ("PASS" if not any(m.startswith("bad") for m in msgs) else "FAILED"))
    return 0 if not any(m.startswith("bad") for m in msgs) else 1


def main():
    tex = sys.argv[1] if len(sys.argv) > 1 else "novel.tex"
    if not os.path.isfile(tex):
        sys.exit("no such file: " + tex)
    eng, exe = engine.pick()
    if not eng:
        sys.exit("no XeLaTeX engine on PATH; run: python build.py --install")
    proj = os.path.dirname(os.path.abspath(tex)) or "."

    src = open(tex, encoding="utf-8").read()
    i = src.find(r"\begin{document}")
    if i < 0:
        sys.exit("cannot find \\begin{document} in " + tex)
    preamble, body = src[:i], src[i:]

    probe = preamble + r"""
\begin{document}
% \typeout must sit INSIDE the StoryParagraph group: the macro closes with
% \endgroup, so any \the\baselineskip read after it is the outer 12pt, not the grid.
\StoryParagraph{0}{\typeout{""" + MARK + r"""leading=\the\baselineskip}探针。}
\typeout{""" + MARK + r"""width=\the\paperwidth}
\typeout{""" + MARK + r"""height=\the\paperheight}
\end{document}
"""
    tmp = tempfile.mkdtemp(prefix="cjkprobe-")
    p = os.path.join(tmp, "probe.tex")
    open(p, "w", encoding="utf-8").write(probe)
    for f in ("fonts", "assets"):
        src_dir = os.path.join(proj, f)
        if os.path.isdir(src_dir) and not os.path.isdir(os.path.join(tmp, f)):
            shutil.copytree(src_dir, os.path.join(tmp, f))

    if eng == engine.PREFERRED:
        cmd = [exe, "-X", "compile", "probe.tex", "--outdir", tmp, "--keep-logs"]
    else:
        cmd = [exe, "-interaction=nonstopmode", "-halt-on-error",
               "-output-directory=" + tmp, "probe.tex"]
    r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    logp = os.path.join(tmp, "probe.log")
    if os.path.isfile(logp):
        out += open(logp, encoding="utf-8", errors="replace").read()
    vals = dict(re.findall(MARK + r"(\w+)=([^\r\n]+)", out))

    msgs = []
    if r.returncode != 0:
        print(out[-3000:])
        sys.exit("probe failed to compile")

    lead = vals.get("leading", "")
    got = None
    m = re.match(r"([\d.]+)pt", lead)
    if m:
        got = float(m.group(1))
    if got is None:
        msgs.append("bad::could not read the baseline from TeX")
    elif abs(got - EXPECT_LEADING) > 0.05:
        msgs.append("bad::baseline is %s, expected %spt -- BodySingleLeading and setstretch no longer cancel out"
                    % (lead, EXPECT_LEADING))
    else:
        msgs.append("ok::baseline %s on the grid" % lead)

    def inch(key):
        m = re.match(r"([\d.]+)(in|pt)", vals.get(key, ""))
        if not m:
            return None
        return float(m.group(1)) if m.group(2) == "in" else round(float(m.group(1)) / 72.27, 2)
    w, h = inch("width"), inch("height")
    if (w, h) != EXPECT_SHEET:
        msgs.append("bad::page is %sx%s, expected %sx%s in" % (w, h, *EXPECT_SHEET))
    else:
        msgs.append("ok::page %sx%s in" % (w, h))

    fonts = os.path.join(proj, "fonts")
    need = ["SourceHanSerifCN-Regular.otf", "SourceHanSansCN-Medium.otf"]
    missing = [f for f in need if not os.path.isfile(os.path.join(fonts, f))]
    if missing:
        msgs.append("bad::missing fonts: " + ", ".join(missing))
    else:
        msgs.append("ok::both Source Han fonts present")

    real_log = os.path.join(proj, "build", os.path.splitext(os.path.basename(tex))[0] + ".log")
    if os.path.isfile(real_log):
        m = re.search(r"Output written on .*?\((\d+) pages?", open(real_log, encoding="utf-8", errors="replace").read())
        if m:
            print("  book: %s pages\n" % m.group(1))
    sys.exit(fail(msgs, True))


if __name__ == "__main__":
    main()
