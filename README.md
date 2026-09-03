# 增肌起步 · 4 天训练计划

完全新手的商用健身房增肌起步计划 · 单文件 HTML · 可勾选打卡 · 移动端 + 打印友好。

> Demo 草案 v0.1 · 用户档案：男 / 20 岁 / 175cm / 65kg / 0 训练经验

## 在线预览

部署到 GitHub Pages 后访问：`https://<你的用户名>.github.io/<仓库名>/`

## 🚀 部署到 GitHub Pages（3 步）

### 方法一：网页拖拽（最简单）

1. 登录 GitHub → 点 `+` → `New repository`
2. 仓库名填 `fitness-plan`（或任意名），选 `Public`，**不要**勾选 Add README
3. 进仓库页面 → 点 `uploading an existing file` 链接
4. 把 `fitness-plan` 文件夹里**这 3 个文件**全部拖进去：
   - `index.html`
   - `README.md`
   - `.nojekyll`
5. 提交（Commit changes）
6. 仓库 `Settings` → `Pages` → Source 选 `Deploy from a branch` → Branch 选 `main` / `(root)` → Save
7. 等 1-2 分钟，刷新 Pages 页面就有链接了 ✅

### 方法二：Git 命令行

```bash
cd fitness-plan            # 进入本目录
git init
git add .
git commit -m "init: 4-day beginner hypertrophy plan"
git branch -M main
git remote add origin https://github.com/<你的用户名>/fitness-plan.git
git push -u origin main

# 然后去 GitHub 仓库 Settings → Pages → Source: main / (root)
```

## ✨ 功能特性

| 能力 | 说明 |
|---|---|
| 📱 移动端响应式 | ≤600px 断点自适应 |
| 🖨️ 打印优化 | 隐藏打卡控件、浅色背景、自动展开所有动作、分页 |
| ✅ 逐组打卡 | 每个动作的每组独立勾选 |
| ✅ 训练日打卡 | 每天训练完一键勾"今日完成" |
| 📊 实时进度条 | 组数 / 训练日 / 百分比三段式 |
| 💾 离线持久化 | localStorage 自动保存，刷新不丢 |
| 🔄 一键重置 | 带二次确认 |
| 🌓 暗色主题 | 黑底橙绿高亮，护眼 |

## 📋 训练内容（4 天循环）

| 训练日 | 部位 | 主题 |
|---|---|---|
| 周一 Day 1 | 胸 + 三头 | 推 · 水平推 + 肘伸 |
| 周二 Day 2 | 背 + 二头 | 拉 · 垂直拉 + 水平拉 + 肘屈 |
| 周四 Day 3 | 肩 + 手臂收尾 | 推 + 拉补充 · 肩部细节 + 二三头补强 |
| 周五 Day 4 | 腿 + 核心 | 下肢 · 髋膝联动 + 躯干稳定 |

24 个动作 / 78 组 / 周三 / 周六 / 周日 休息

每个动作都包含：组数 × 次数、强度（RPE）、节奏、休息、4 条要点、3 条常见错误、2 个替代动作。

## ⚠️ 关于膝盖

`腿日`（周五）热身中含 ⚠️ 膝盖提示，建议膝盖不适时优先哈克深蹲 / 高脚杯深蹲 / 腿举机，**深蹲下蹲不超过膝盖水平线，任何动作出现膝痛立即停止**。详见页脚"通用训练原则 → 膝盖友好"。

## 🔧 本地定制

- **改用户信息**：编辑 `index.html`，搜 `PROFILE` 不会找到（HTML 是渲染后的），改为搜索 `profile-grid` 段落直接改值。
- **改训练内容**：建议保留生成器 `generate_plan.py`（在原 Codex 工作目录 `work/` 下），改数据后重新生成 `index.html`。
- **换色系**：搜 `:root` 块，修改 CSS 变量（`--accent`、`--success` 等）。

## 📁 文件清单

```
fitness-plan/
├── index.html      # 主页面（约 68 KB，含 CSS+JS 全内嵌）
├── README.md       # 本文件
└── .nojekyll       # 跳过 Jekyll 解析
```

单文件部署，零依赖，零构建。
