---
name: cjk-novel
description: Typeset Chinese fiction or narrative prose into a 5 x 8 inch trade paperback PDF. Compiles with tectonic when available and falls back to xelatex, so it also works on machines that already have TeX Live or MiKTeX. Ships a working template (Source Han Serif body, Source Han Sans heads), a two-ink palette, running heads, optional cover page, and three paragraph macros that encode narrative rhythm - StoryParagraph{space}{text}, NarrativeBreak, UnprintedPause. Also checks and helps set up the XeLaTeX environment. Use when asked to 排版成小开本, 出书, 把稿子排成 PDF, 排一本小说, make a book/novella PDF, set Chinese prose in a 5x8 book layout, or when a LaTeX/xelatex/tectonic setup question comes up in this context.
license: Template and scripts MIT; bundled Source Han fonts under SIL OFL 1.1 (see assets/fonts/*LICENSE.txt).
compatibility: Needs one of tectonic (preferred) or xelatex on PATH. `python scripts/build.py --install` installs tectonic via scoop/choco/brew/apt/cargo; `doctor` reports what is missing. Nothing else is required.
---

# 中文小说 5x8 小开本排版

## First-time setup - do this before anything else

The skill will not work until a XeLaTeX engine is on PATH. Check first, always:

```bash
python <skill>/scripts/build.py doctor
```

It prints one line per thing and ends with `ready` or `not ready yet`:

| line | meaning |
|---|---|
| `engine MISSING` | neither tectonic nor xelatex is installed |
| `bundle cold` | first build will download macros one by one (~44 MB); needs network |
| `tempdir FAIL` | no writable temp directory |
| `body/head font MISSING` | the two Source Han OTF files are gone from `assets/fonts/` |

**If an engine is missing, ask the user before installing anything.** Installing
software changes their machine and is their call, not yours. Once they agree:

```bash
python <skill>/scripts/build.py --install
```

That installs tectonic with whichever package manager is present (scoop, choco, brew,
apt/dnf/pacman, cargo) and prints what it ran. Then re-run `doctor`.

If the user would rather not install anything, they may already have TeX Live or
MiKTeX — `xelatex` works just as well and the skill will use it automatically. Do not
push them toward installing tectonic if `xelatex` is already there.

## Workflow

**New book:**

```bash
python <skill>/scripts/build.py --init my-book   # copies template + 20 MB of fonts
# edit my-book/novel.tex: set \BookTitle, \BookAuthor, then write the text
cd my-book && python <skill>/scripts/build.py novel.tex
python <skill>/scripts/verify.py novel.tex
```

**Existing project:** put `novel.tex` in, make sure `fonts/` holds the two OTF files,
then build. `build.py` picks `novel.tex`, `main.tex` or the only `.tex` in the folder.

Useful flags: `--xelatex` (force the fallback), `--offline` (fail rather than hit the
network, useful once the bundle is cached), `-o DIR` (output folder).

Both engines are one command. tectonic reruns itself when cross-references change;
the xelatex path runs twice on its own.

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

## Troubleshooting

| symptom | cause and fix |
|---|---|
| `Fontconfig error: Cannot load default config file` (Windows) | harmless; fonts load from `./fonts/`, not the system |
| compile dies on `connection`, `timed out`, `dns`, `proxy` | no network, and tectonic fetches macros on demand. Retry, or pass `--bundle <URL>` to point at a mirror |
| `--offline` fails on a cold cache | expected; run one build with network first |
| font not found | `fonts/` is missing an OTF; `python scripts/build.py --init .` in a fresh folder copies both back |
| `engine MISSING` but the user says they installed it | PATH differs between their shell and this agent's environment; ask them to run `tectonic --version` in their own terminal |
| `book.py`/`xelatex` not found on macOS/Linux | install `tectonic` (`brew`, `apt`, `dnf`, `pacman`) or a TeX distribution providing `xelatex` |

## Notes

- `build/` is gitignored by the scaffold; PDFs land there.
- Body is 9.5pt Source Han Serif; heads and running heads are Source Han Sans.
  Colours: `PrimaryInk` #161618, `SecondaryInk` #5C5C62.
- The template contains no book text. Dropping prose into `\StoryParagraph` is all
  it takes to typeset a manuscript.
