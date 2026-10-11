# cjk-novel

[中文](README.md)

An agent skill that typesets Chinese fiction into a **5 x 8 inch trade paperback PDF**.

It ships a working XeLaTeX template (Source Han Serif body, Source Han Sans heads),
a two-ink palette, running heads, optional cover page, widow/orphan control, and the
three paragraph macros that carry the narrative rhythm. Compiled with
[tectonic](https://tectonic-typesetting.github.io/), a lightweight XeTeX engine, so
there is no TeX Live to install.

```
$ python scripts/build.py --init my-book
$ cd my-book && python ../scripts/build.py novel.tex
OK  22 pages  ->  .../build/novel.pdf     # page count follows from your text
```

## Why this exists

The layout was reverse-engineered from a hand-tuned 5 x 8 edition, and the part that
was easy to lose was *why* the preamble looks the way it does. It carries a baseline
grid with a compensated value:

```
BodySingleLeading = 17.3076923   is not the leading
17.3076923 x \setstretch{1.3}  = 22.5pt   is
```

Change the font size or the setstretch without touching `\BodySingleLeading` and the
grid silently stops being 22.5pt. The PDF still builds. Nothing warns you. So
`scripts/verify.py` compiles a throwaway probe and asks TeX for the real numbers:

```
ok   baseline 22.50005pt on the grid
ok   page 5.0x8.0 in
ok   both Source Han fonts present
```

## Install

Clone it straight into a skills directory:

```bash
git clone https://github.com/jefeerzhang/cjk-novel.git \
    ~/.agents/skills/cjk-novel
```

That works for prime-agent and any other Agent Skills compatible loader. Restart the
agent afterwards so it rescans the skills directory.

Requires the `tectonic` binary:

```bash
scoop install tectonic      # Windows
choco install tectonic
cargo install tectonic
```

First run downloads the TeX bundle (~100 MB) and caches it; later runs work offline.

## The three macros

```latex
\StoryParagraph{3}{...}   % paragraph, 3pt of air after it
\StoryParagraph{0}{...}   % paragraph, no air — runs straight on
\UnprintedPause           % blank space, no symbol at all
\NarrativeBreak           % centred three dashes, changes scene
```

The number in `\StoryParagraph` is the breathing. Short lines take `0`; a line that
should sit on its own takes `3`. Do not normalise it away.

## Layout constants

| | |
|---|---|
| Page | 5 x 8 in, inner/outer margin 0.5 in, top/bottom 0.7 in |
| Body | Source Han Serif 9.5pt, leading 22.5pt |
| Heads | Source Han Sans 8pt |
| Ink | `PrimaryInk` #161618, `SecondaryInk` #5C5C62 |

Measured, do-not-guess constants live in `assets/novel.tex`: the `70.817pt` opening
breathing space, `37.4pt`/`31.4pt` around `\NarrativeBreak`, `22pt` for
`\UnprintedPause`, and `\addtolength{\textheight}{-12pt}`. Change the page size or
margins and they have to be re-measured against the output.

## Credits

The template is adapted from
[HEJustinSun/my-girlfriend-jingtian-latex](https://github.com/HEJustinSun/my-girlfriend-jingtian-latex),
the XeLaTeX edition of 《我的女友景甜》 by 孙宇晨. That project's public repository
contains the source the geometry, palettes and macros were derived from; none of its
text is included here.

## Licence

Skill code and template: MIT. Bundled Source Han fonts: SIL Open Font License 1.1,
see `assets/fonts/`.
