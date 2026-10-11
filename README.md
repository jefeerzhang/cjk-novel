# cjk-novel

把中文小说排成 **5 × 8 英寸小开本 PDF** 的 agent skill。

内置一份能直接用的 XeLaTeX 模板（正文思源宋体、标题与页眉思源黑体）、双色墨配色、
页眉页码、可选封面插页、孤行寡行控制，以及承载叙事节奏的三个段落宏。用
[tectonic](https://tectonic-typesetting.github.io/) 编译——一个轻量的 XeTeX 引擎，
**不需要装 TeX Live**。

[English](README.en.md)

```
$ python scripts/build.py --init my-book
$ cd my-book && python ../scripts/build.py novel.tex
OK  22 pages  ->  .../build/novel.pdf     # 页数取决于你写了多少字
```

## 为什么会有这个 skill

这套版式是从一本手工调校过的 5 × 8 开本里反推出来的，而最容易在转手时丢掉的部分，
是 preamble 里那些数字**为什么长这样**。它带着一套基线网格，其中一个值是经过补偿的：

```
BodySingleLeading = 17.3076923   ← 它本身不是行距
17.3076923 × \setstretch{1.3}  =  22.5pt  ← 这个才是
```

如果你改了字号或 `\setstretch` 却没同步改 `\BodySingleLeading`，网格就不再是 22.5pt。
**PDF 照样能编译出来，没有任何报错，也没有人会提醒你。**

所以 `scripts/verify.py` 会编译一个一次性的探针文档，直接向 TeX 索要真实数值：

```
ok   baseline 22.50005pt on the grid
ok   page 5.0x8.0 in
ok   both Source Han fonts present
```

## 环境配置

**先跑体检，再干别的：**

```bash
python scripts/build.py doctor
```

它会逐项报出缺什么，最后给一句结论：

```
cjk-novel environment

  engine      ok    tectonic  (Tectonic 0.17.0)
  bundle      ok    C:\Users\...\TectonicProject\Tectonic  (44 MB cached)
  tempdir     ok    C:\Users\...\Temp
  body font   ok    assets/fonts/SourceHanSerifCN-Regular.otf
  head font   ok    assets/fonts/SourceHanSansCN-Medium.otf

ready
```

| 结论行 | 含义 |
|---|---|
| `engine MISSING` | tectonic 和 xelatex 都没装 |
| `bundle cold` | 首次编译要逐个下载宏包（约 44 MB），需要联网 |
| `tempdir FAIL` | 没有可写的临时目录 |
| `body/head font MISSING` | `assets/fonts/` 里的思源字体不见了 |

**引擎怎么来。** 优先级是 **tectonic → xelatex**：

- 有 **tectonic**（推荐）：一个二进制，不用装 TeX Live，会自动跑第二遍
- 有 **xelatex**：很多机器本来就装了 TeX Live 或 MiKTeX，**直接就能用，skill 会自动回退**，
  跑两遍。已经有 TeX 环境就不必再装 tectonic

两个都没有时，装 tectonic：

```bash
python scripts/build.py --install
```

它会自动挑本机有的包管理器（scoop / choco / brew / apt / dnf / pacman / cargo）来装，
并把执行的命令打出来。也可以手动装：

```bash
scoop install tectonic      # Windows，免管理员
choco install tectonic
brew install tectonic       # macOS
apt install tectonic        # Debian/Ubuntu
cargo install tectonic      # 已有 Rust
```

## 安装本 skill

直接克隆进 skills 目录：

```bash
git clone https://github.com/jefeerzhang/cjk-novel.git \
    ~/.agents/skills/cjk-novel
```

prime-agent 和其他兼容 Agent Skills 规范的 loader 都能用。装完**重启 agent**，
它才会重新扫描 skills 目录。

## 使用

```bash
python scripts/build.py --init my-book     # 脚手架：模板 + 20 MB 字体
cd my-book
# 改 \BookTitle 和 \BookAuthor，然后写正文
python ../scripts/build.py novel.tex
python ../scripts/verify.py novel.tex
```

常用参数：`--xelatex`（强制走回退）、`--offline`（资源已缓存时禁止联网）、
`-o DIR`（换输出目录）。

## 三个段落宏

```latex
\StoryParagraph{3}{...}   % 段落，段后留 3pt 气口
\StoryParagraph{0}{...}   % 段落，段后不留，紧接下一段
\UnprintedPause           % 只留空白，不给任何符号
\NarrativeBreak           % 居中三短横，断场景
```

`\StoryParagraph` 里那个数字就是**呼吸**。短句用 `0`，需要单独成段、悬在一行的那句用 `3`。
不要把它统一掉。

## 版面常数

| | |
|---|---|
| 页面 | 5 × 8 英寸，订口/切口 0.5 英寸，天头/地脚 0.7 英寸 |
| 正文 | 思源宋体 9.5pt，行距 22.5pt |
| 页眉标题 | 思源黑体 8pt |
| 墨色 | `PrimaryInk` #161618，`SecondaryInk` #5C5C62 |

`assets/novel.tex` 里还有几个**实测得来、不要凭感觉改**的常数：开篇留白 `70.817pt`、
`\NarrativeBreak` 上下各 `37.4pt` / `31.4pt`、`\UnprintedPause` 的 `22pt`，以及
`\addtolength{\textheight}{-12pt}`。改动页面尺寸或页边距后，这些值必须对着输出的 PDF
重新量，不能估。

## 排错

| 现象 | 原因和对策 |
|---|---|
| Windows 打印 `Fontconfig error: Cannot load default config file` | **无害**。字体从 `./fonts/` 读，不走系统字体查找 |
| 编译卡在 `connection` / `timed out` / `dns` / `proxy` | 没网，而 tectonic 按需下载宏包。换网络重试，或用 `--bundle <URL>` 指向镜像源 |
| `--offline` 在冷缓存下失败 | 预期行为。先联网完整跑一次 |
| 字体找不到 | `fonts/` 少了 OTF。在干净目录里 `python scripts/build.py --init .` 把两个字体拷回去 |
| `engine MISSING` 但用户说他装了 | agent 的 PATH 和用户终端的 PATH 不一致。让用户在自己终端里跑 `tectonic --version` 确认 |

## 致谢

模板改编自
[HEJustinSun/my-girlfriend-jingtian-latex](https://github.com/HEJustinSun/my-girlfriend-jingtian-latex)
——孙宇晨《我的女友景甜》的 XeLaTeX 版。本仓库的版心、配色和段落宏都源自那个项目，
但**不含其中任何正文内容**。

## 许可

skill 代码与模板：MIT。
`assets/fonts/` 内的思源宋体与思源黑体：SIL Open Font License 1.1，
见 `assets/fonts/*LICENSE.txt`。
