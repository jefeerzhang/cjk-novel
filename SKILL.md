---
name: cjk-novel
description: Typeset Chinese fiction or narrative prose into a 5 x 8 inch trade paperback PDF with XeLaTeX and the lightweight tectonic engine. Ships a working template (Source Han Serif body, Source Han Sans heads), a two-ink palette, running heads, optional cover page, and three paragraph macros that encode narrative rhythm - StoryParagraph{space}{text}, NarrativeBreak, UnprintedPause. Use when asked to 排版成小开本, 出书, 把稿子排成 PDF, 排一本小说, make a book/novella PDF, or set Chinese prose in a 5x8 book layout.
license: Template and scripts MIT; bundled Source Han fonts under SIL OFL 1.1 (see assets/fonts/*LICENSE.txt).
compatibility: Needs the tectonic binary on PATH (scoop install tectonic / choco install tectonic / cargo install tectonic). First run downloads the TeX bundle (~100 MB), later runs work offline.
---

# 中文小说 5x8 小开本排版

## What this gives you

A working XeLaTeX template for Chinese fiction, plus two scripts. Everything below
is already solved: local CJK fonts, page geometry, a baseline grid, running heads,
cover insertion, widow/orphan control, and the paragraph macros the original style
was built around.

## Workflow

**New book:**

```bash
python <skill>/scripts/build.py --init my-book   # copies template + 20 MB of fonts
# edit my-book/novel.tex: set \BookTitle, \BookAuthor, then write the text
cd my-book && python <skill>/scripts/build.py novel.tex
```

**Existing project:** drop `novel.tex` in, make sure `fonts/` holds the two OTF
files, then `python <skill>/scripts/build.py novel.tex`.

Then always run the check:

```bash
python <skill>/scripts/verify.py novel.tex
```

tectonic reruns TeX by itself when cross-references change, so one build is enough.

## The three macros

```latex
\StoryParagraph{3}{正文}      % 段后留 3pt 气口
\StoryParagraph{0}{正文}      % 段后 0pt，紧接下一段
\UnprintedPause               % 只留空白，不给任何符号
\NarrativeBreak               % 居中三短横，断场景
```

The number in `\StoryParagraph` is deliberate: it is how the prose breathes.
Short lines get 0, a line that should sit alone gets 3. Do not normalise it away.

## The baseline grid - read before changing type sizes

`\BodySingleLeading` is **17.3076923 and that is not the leading**. `\setstretch{1.3}`
multiplies the `\fontsize` baseline a second time, so the line spacing actually on
the page is:

```
17.3076923 x 1.3 = 22.5pt
```

To change the leading, pick a target `L` and write `L/1.3`, e.g. 24pt leading means
`\newcommand{\BodySingleLeading}{24/1.3}`. If you edit the font size or the
setstretch without touching `\BodySingleLeading`, the grid stops being 22.5pt and
nothing warns you. `verify.py` exists to catch exactly that.

22.5pt was chosen as the page grid. Changing it is a re-layout job, not a tweak.

## What is not negotiable without a re-layout

`\vspace*{70.817pt}` (opening page), `37.4pt` / `31.4pt` (around `\NarrativeBreak`),
`22pt` (`\UnprintedPause`), and `\addtolength{\textheight}{-12pt}` are all
measured from a real layout. Change page size or margins and they have to be
re-measured against the output PDF, not guessed.

## Notes

- Windows prints `Fontconfig error: Cannot load default config file` on every run.
  Harmless: fonts come from `./fonts/`, not from the system.
- `build/` is gitignored by the scaffold; PDFs live there.
- Body is 9.5pt Source Han Serif; heads and running heads are Source Han Sans.
  Colours: `PrimaryInk` #161618, `SecondaryInk` #5C5C62.
