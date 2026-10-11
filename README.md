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

## 安装

直接克隆进 skills 目录即可：

```bash
git clone https://github.com/jefeerzhang/cjk-novel.git \
    ~/.agents/skills/cjk-novel
```

prime-agent 和其他兼容 Agent Skills 规范的 loader 都能用。装完**重启 agent**，
它才会重新扫描 skills 目录。

需要 `tectonic` 可执行文件：

```bash
scoop install tectonic      # Windows
choco install tectonic
cargo install tectonic
```

首次运行会下载 TeX 资源包（约 100 MB）并缓存，之后离线可用。

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

## 已知噪音

Windows 上每次编译都会打印 `Fontconfig error: Cannot load default config file`。
**无害**：字体是从 `./fonts/` 读的，不走系统字体查找。

## 致谢

模板改编自
[HEJustinSun/my-girlfriend-jingtian-latex](https://github.com/HEJustinSun/my-girlfriend-jingtian-latex)
——孙宇晨《我的女友景甜》的 XeLaTeX 版。本仓库的版心、配色和段落宏都源自那个项目，
但**不含其中任何正文内容**。

## 许可

skill 代码与模板：MIT。
`assets/fonts/` 内的思源宋体与思源黑体：SIL Open Font License 1.1，
见 `assets/fonts/*LICENSE.txt`。
