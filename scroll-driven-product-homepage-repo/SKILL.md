---
name: scroll-driven-product-homepage
description: 把本地项目/产品打包成一镜到底的滚动驱动可视化主页（scroll-scrub 单页官网）。用于「把 X 做成个人主页/产品官网」「滚动一镜到底展示各产品元素」「加侧边快速索引条」这类需求：内置 oil-motion 的 Concept Contract→预算→timeline 编译流程、章节锚点索引同步、WCAG 对比度实算校验、agent-browser 截图与踩坑规避。产出单文件 HTML + 本地截图资产。附带零依赖脚本：timeline 编译器、对比度计算器、本地预览服务。
agent_created: true
---

# 滚动驱动产品主页构建

把「已有若干本地产品元素（数据库目录 / 本地服务 / 面板）」打包成一镜到底的滚动官网。

## 何时使用

- 用户说「把我目前 X 产品打包成可视化可互动个人主页 / 官网」
- 需求包含「往下滚动一镜到底，每滚动一次显示一个产品元素」
- 「加侧边栏快速索引条方便查找」
- 「不用把每条数据都滚动显示，只要名称 + 大概内容 + 访问链接」
- 要求与某公司/品牌关联，体现产品针对性

不适用：纯静态介绍页（无滚动叙事）、需要生成视频素材的影片级动画（走 oil-motion 主流程）。

## 环境前提（Windows）

**Bash 工具 PATH 缺失是本机高频坑**：默认 `ls`/`head`/`dirname`/`cat` 全部 `command not found`。
所有 Bash 调用前必须加：

```bash
export PATH="/usr/bin:/bin:/c/Windows/System32:$PATH"
```

Node：`C:/Users/<user>/.workbuddy/binaries/node/versions/<ver>/node.exe`
Python：`C:/Users/<user>/.workbuddy/binaries/python/versions/<ver>/python.exe`

## 执行流程

### 阶段 1 · 探明资产（并行）

1. 用 `Glob`/`Bash(export PATH...)` 列出产品元素目录结构，读关键内容文件（不只读目录名）。
2. `curl -s -o /dev/null -w "%{http_code}"` 探测各本地服务是否在线。
3. `curl -s <url> | head -c N` 抓首页，**提取其真实设计 token**（主色、圆角、字体），
   让新主页与既有产品视觉同源，而不是凭空配色。

### 阶段 2 · 问清选项（用 AskUserQuestion，一次问完）

默认要问的三项（照此措辞可直接用）：

1. **呈现深度**：真实数据看板（推荐，把真实数据做成图表/卡片，可点击跳转）vs 只做入口导航
   （仅名称+简介+链接）。
2. **索引导航**：左侧圆点+文字标签（推荐）vs 左侧完整列表 vs 右侧竖向进度。
3. **视觉基调**：深色科技感（推荐）vs 浅色官网风。

用户已明确指定的项不要重复问。

### 阶段 3 · oil-motion 四事实源

建目录 `source/ build/ final/ qa/`，写：

- `source/concept-contract.yaml` —— 用户原话不改写。关键字段：
  `driver: scroll` / `input_semantics: continuous` / `time_control: scrub` /
  `navigation: continuous` / `aspect_ratio: 16:9` / `background_owner: page` /
  `media_source: none`（纯程序动画，无生成媒体）。
- `source/motion-brief.yaml` —— 派生计划，`keyframes: []`、`clip_chain: []`。
- 跑预算（`--background-owner` 与 `--time-control` 必须显式传，无默认值）：

```bash
python "$OIL_MOTION/scripts/motion_budget.py" \
  --frames <章节数> --display "1920x1080" --dpr 2 \
  --driver scroll --time-control scrub --parameter-space linear \
  --background-owner page --scroll-pages <章节数> --frames-per-page 1 \
  --report build/motion-budget.json --strict --json
```

必须看到 `failures: []`。记下 `runtime.controller`（scrub → `frame-scrub`）。

- **编译时间轴** —— 用 `scripts/compile_timeline.py`：

```bash
# 用章节配置（推荐）
python scripts/compile_timeline.py --chapters chapters.json --out build/timeline.json

# 或命令行直接给：'id:标签[:权重]'
python scripts/compile_timeline.py \
  --section hero:首页:1.0 --section detail:详情:1.35 \
  --out build/timeline.json
```

`chapters.json` 为数组，`weight` 控制该章节占整页的滚动比例：

```json
[
  {"id": "hero",     "label": "首页",     "sub": "品牌露出", "weight": 1.0},
  {"id": "overview", "label": "产品总览", "sub": "三大模块", "weight": 0.85},
  {"id": "detail",   "label": "详情",     "sub": "数据看板", "weight": 1.35}
]
```

脚本**内建硬性断言**，任一失败即拒绝写出文件：

- 段内 `start <= hold < endExclusive`
- `from → to` 连链不断、无重叠、无空隙
- state id 非空且唯一，状态数 = 段落数
- 末段 `endExclusive` 必须收敛到 `1.0`

### 阶段 4 · 写单文件 HTML（`final/index.html`）

结构：固定顶栏 + 固定左侧索引条 + `.stage` 内 N 个 `<section class="chapter" data-chapter="<state id>">`。

**索引同步的正确做法**（关键，易错）：

```js
// 每个章节的归一化滚动锚点
function measureAnchors() {
  const max = docEl.scrollHeight - docEl.clientHeight;
  sectionAnchors = sections.map(el => clamp(el.offsetTop / max, 0, 1));
}
// 进度落在哪个章节区间就激活哪个 —— 不要用 timeline.hold 当阈值！
function stateForProgress(p) {
  for (let i = sectionAnchors.length - 1; i >= 0; i--)
    if (p >= sectionAnchors[i] - 1e-6) return i;
  return 0;
}
```

❌ **反模式**：用 `timeline.hold`（章节内 45% 处）当激活阈值 → 因为 `scrollIntoView`
对齐的是章节**顶部**，索引必然落后一整章。

其他实现要点：

- `scroll` 事件只置 `pending`，渲染集中到 `requestAnimationFrame`（每帧最多一次 DOM 写）。
- `IntersectionObserver` 做入场 reveal，进入即 `unobserve`（离屏停止计算）。
- `ResizeObserver` 监听 `body` 重算锚点。
- 初始化时比对 `timeline.states[].id` 与 DOM `[data-chapter]`，不一致就报错并禁用同步。
- `prefers-reduced-motion`：关闭位移动画，reveal 直接置 `in`，`scroll-behavior: auto`。
- 布局：CSS Grid `repeat(auto-fit, minmax(260px,1fr))`；内容区最大宽 ~1180px；
  索引条宽度用 CSS 变量，窄屏（≤1200px）隐藏并让内容占满。

### 阶段 5 · 截图真实界面（agent-browser）

```bash
npm install -g agent-browser && agent-browser install   # 首次
```

**必须遵守**（否则页面会变空白 / 命令被 SIGTERM）：

1. 命令输出**重定向到日志再 cat**，不要直接管道：
   `agent-browser open "<url>" > qa/ab.log 2>&1; cat qa/ab.log`
2. **每张截图用全新 session**，不要在同一 session 里连续 eval/scroll/screenshot：
   `agent-browser --session s1 open "<url>"` → `wait 3400` → `eval "window.scrollTo(...)"`
   → `wait 2000` → `screenshot "<path>"`
   （同一 session 二次操作后 `document.body` 常归空，截图变成 3.3KB 白图）
3. 截图后**必须 Read 图片确认**：正常应 >50KB 且非纯白；3.3KB 即为失败需重截。
4. 抓取前先 `eval "document.body.innerText.slice(0,300)"` 确认页面真的渲染了。
5. 全部结束后 `agent-browser close`。

本地预览服务：用 `scripts/serve.js` 起 HTTP（`file://` 在部分场景易空白）：

```bash
node scripts/serve.js ./final 8899
```

服务已带 `Content-Length` 与目录穿越防护。若是自己手写服务，**必须带 `Content-Length`**，
否则二进制图片可能读取异常（实测表现为浏览器内 `naturalWidth` 为 0）：

```js
res.writeHead(200, { 'Content-Type': m, 'Content-Length': d.length });
```

### 阶段 6 · QA 与验收

**对比度必须实算，不能估算** —— 用 `scripts/contrast.py` 跑一遍，逐色核对：

```bash
python scripts/contrast.py                      # 内置色板体检
python scripts/contrast.py "#12211b" "#ffffff"  # 自定义：前景色... + 末尾背景色
```

实测血泪教训：
- 凭感觉写的 `#6b7f77` 实算 **4.26:1**、`#9aa8a2` 实算 **2.47:1（FAIL）**。
- **最容易漏的是渐变按钮上的白字**：默认品牌色渐变浅端（如 `#22bd6d`）上白字只有
  **2.45:1（FAIL）**。凡是白字压渐变，必须**逐个停靠点**算，然后整体压深到
  `brand-800→700→600` 这类深区间，使全程 ≥4.5:1。
- 调色后要**全量替换**（含 SVG 描边、条形渐变、`linear-gradient` 停靠点），
  否则漏改处仍不达标。改完重跑 `contrast.py` 确认。

其他验收项：
- 无横向溢出（比对 `scrollWidth` vs `clientWidth`，桌面 + 375px 移动端）
- 无 JS 报错、`[data-chapter]` 数与索引条项数一致
- 截图 `naturalWidth > 0` 且 `closest('.browser-body')` 未标 `failed`
- 键盘可达、`aria-current` 标记当前项、图表 `role="img"` + 数据化 `aria-label`

输出 `qa/qa-report.md`，按表格逐项给实测值。

### 阶段 7 · 交付

`present_files` 传 `final/index.html`（首选，HTML 会开实时预览）+ 关键截图。
保留 `source/ build/ final/ qa/` 四目录。

## 金融/企业数据类额外约定

- 涨跌配色用**中国市场惯例：红涨绿跌**（`--up` 红 / `--down` 绿），与欧美相反。
- 金额默认 `¥` / 亿元；港股用 `HK$`。
- 每条数据标注来源与更新日期；口径不同（如不同咨询机构市占率）必须显式注明不可直接对比。

## 常见故障速查

| 现象 | 原因 | 处置 |
|---|---|---|
| `ls: command not found` | 未导出 PATH | 命令前 `export PATH="/usr/bin:/bin:/c/Windows/System32:$PATH"` |
| agent-browser 无输出 / SIGTERM | 直接管道 | 重定向到日志文件再 cat |
| 截图 3.3KB 纯白 | 同 session 复用后页面归空 | 换新 `--session`，且 open 后先 wait |
| 索引条高亮滞后一章 | 用 `hold` 当阈值 | 改用章节 `offsetTop/maxScroll` 锚点 |
| 标题字块被切碎 | 强制 `<br>` + 窄栏 | 只在宽屏强制两行，窄屏自然折行 |
| 图片 `size=0` | 响应缺 `Content-Length` | 补 `Content-Length: d.length` |
| 对比度不达标 | 凭感觉配色 | 实算后调深并全量替换 |
| 白字压在渐变上发灰 | 只算了单一色值，漏算渐变浅端 | 逐停靠点实算，整体压深到深色区间 |
