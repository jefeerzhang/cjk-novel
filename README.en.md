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

## Setup

**Run the doctor before anything else:**

```bash
python scripts/build.py doctor
```

```
cjk-novel environment

  engine      ok    tectonic  (Tectonic 0.17.0)
  bundle      ok    /home/you/.cache/Tectonic  (44 MB cached)
  tempdir     ok    /tmp
  body font   ok    assets/fonts/SourceHanSerifCN-Regular.otf
  head font   ok    assets/fonts/SourceHanSansCN-Medium.otf

ready
```

It ends with `ready` or `not ready yet`. The lines that matter:

| line | meaning |
|---|---|
| `engine MISSING` | neither tectonic nor xelatex is installed |
| `bundle cold` | the first build downloads macros one by one (~44 MB); needs network |
| `tempdir FAIL` | no writable temp directory |
| `body/head font MISSING` | the two Source Han OTF files are gone |

**Engines.** Preference order is **tectonic, then xelatex**:

- **tectonic** (preferred): one binary, no TeX Live, reruns itself
- **xelatex**: plenty of machines already have TeX Live or MiKTeX. **The skill falls
  back to it automatically** and runs two passes. If you already have a TeX setup there
  is nothing to install.

With neither present, install tectonic:

```bash
python scripts/build.py --install
```

It picks whichever package manager you have (scoop, choco, brew, apt/dnf/pacman, cargo)
and prints the command it runs. Or do it yourself:

```bash
scoop install tectonic      # Windows, no admin
choco install tectonic
brew install tectonic       # macOS
apt install tectonic        # Debian/Ubuntu
cargo install tectonic      # if you already have Rust
```

## Install this skill

```bash
git clone https://github.com/jefeerzhang/cjk-novel.git \
    ~/.agents/skills/cjk-novel
```

Works with prime-agent and any other Agent Skills compatible loader. Restart the agent
afterwards so it rescans the skills directory.

## Usage

```bash
python scripts/build.py --init my-book     # template + 20 MB of fonts
cd my-book
# set \BookTitle and \BookAuthor, then write the text
python ../scripts/build.py novel.tex
python ../scripts/verify.py novel.tex
```

Flags: `--xelatex` (force the fallback), `--offline` (never hit the network once the
bundle is cached), `-o DIR` (output folder).

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

## Troubleshooting

| symptom | cause and fix |
|---|---|
| `Fontconfig error: Cannot load default config file` (Windows) | harmless; fonts load from `./fonts/`, not the system |
| compile dies on `connection`, `timed out`, `dns`, `proxy` | no network, and tectonic fetches macros on demand. Retry, or pass `--bundle <URL>` to point at a mirror |
| `--offline` fails on a cold cache | expected; run one build with network first |
| font not found | `fonts/` is missing an OTF; `python scripts/build.py --init .` in a fresh folder copies both back |
| `engine MISSING` but the user says they installed it | PATH differs between their shell and this agent's environment; ask them to run `tectonic --version` in their own terminal |

## Credits

The template is adapted from
[HEJustinSun/my-girlfriend-jingtian-latex](https://github.com/HEJustinSun/my-girlfriend-jingtian-latex),
the XeLaTeX edition of 《我的女友景甜》 by 孙宇晨. That project's public repository
contains the source the geometry, palettes and macros were derived from; none of its
text is included here.

## Licence

Skill code and template: MIT. Bundled Source Han fonts: SIL Open Font License 1.1,
see `assets/fonts/`.
