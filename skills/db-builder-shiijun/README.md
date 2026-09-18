# 数据库搭建工作流 (识君版) — db-builder-shiijun

> **为任意 A 股 / 港股 / 美股上市公司搭建一套完整的"数据抓取 → 结构化存储 → 可视化展示 → 知识库沉淀 → 自动化更新"端到端工作流。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1-blue.svg)]()
[![WorkBuddy Skill](https://img.shields.io/badge/WorkBuddy-Skill-green.svg)]()

---

## 📖 简介

本 SKILL 是 [WorkBuddy](https://workbuddy.ai) 平台的官方 skill 之一，由 [@识君](https://github.com/gaobin922) 在搭建蒙牛集团 (02319.HK) 数据库项目过程中沉淀和开源。

**验证项目**：
- 蒙牛乳业 (02319.HK) — 5 年财务 + 3 家竞品 + 6 家控股 + 7 个高级分析维度
- 37 篇 Obsidian 笔记 · 3 个 plotly 交互仪表板 · 工作日 16:10 自动更新

**复用度**：⭐⭐⭐⭐⭐
- 适用：任意上市公司（A股/港股/美股/行业链/金融机构）
- 投入：3-4 小时可完成新公司整套数据库
- 输出：可立即使用的可检索、可视化、自动化知识库

---

## 🎯 触发场景

```text
"帮我搭建 XX 公司数据库"
"抓取 XX 公司年报/中报"
"做一份 XX 财务仪表板"
"把 XX 数据加入 Obsidian"
"每日自动更新 XX 数据"
"分析 XX 与 YY 的竞争"
"我想长期跟踪 XX 公司"
```

---

## 🚀 快速使用

### 1. 安装到 WorkBuddy

将整个 `db-builder-shiijun/` 目录复制到：
- 用户级：`~/.workbuddy/skills/db-builder-shiijun/`
- 项目级：`./.workbuddy/skills/db-builder-shiijun/`

### 2. 在对话中触发

直接对 WorkBuddy 说：
```
请用 db-builder-shiijun skill 帮我搭建"伊利股份 (600887.SH)"数据库
```

WorkBuddy 会自动：
1. 加载本 skill 的 12 阶段工作流
2. 用 AskUserQuestion 问 4 个关键决策（维度/范围/历史跨度/Obsidian 集成）
3. 依次执行抓取 → 解析 → 可视化 → 知识库 → 自动化
4. 输出完整可用的数据库 + 工作流 prompt 词

### 3. 完整工作流

| 阶段 | 输出 |
|---|---|
| 0. 问询 | 4 决策 |
| 1. 加载技能 | cn-financial-scraper + data-visualization + obsidian |
| 2. 目录规划 | E:\WB outputs\公司_db\ + Obsidian 子目录 |
| 3. 财务抓取 | 5 年 PDF + JSON |
| 4. 行情抓取 | 实时+历史 |
| 5. 行业抓取 | 市占率+政策 |
| 6. 控股抓取 | 子公司年报 |
| 7. ESG 抓取 | MSCI/恒生/标普评级 |
| 8. 研报抓取 | 26+ 券商评级 |
| 9. HTML 仪表板 | plotly 交互 |
| 10. Obsidian 笔记 | 8+ 篇 |
| 11. 自动化配置 | 工作日 16:10 |
| 12. Prompt 词编写 | 跨项目复用 |

---

## 📦 仓库内容

```
db-builder-shiijun/
├── SKILL.md                       # Skill 主体（imperative 形式 + 中文）
├── LICENSE                        # MIT 许可证
├── README.md                      # 本文件
├── references/
│   ├── scripts-collection.md      # 完整抓取脚本合集
│   └── obsidian-template.md       # Obsidian 笔记模板
└── templates/
    └── dashboard-template.py       # Plotly 仪表板模板
```

---

## 🛠️ 关键技术（避坑指南）

### 1. cninfo API 正确姿势

```python
# ❌ 错误：用 'stock=orgId,code' 或 'searchkey=年度报告' → 找不到
# ✅ 正确：用 secid + stock 组合
data = {'stock': f'600887,gssh0600887', 'tabName': 'fulltext',
        'pageSize': 50, 'column': 'sse', 'plate': 'sse',
        'seDate': '2025-04-01~2025-05-30'}
```

### 2. PDF 中文解析

```python
# ❌ pypdf 解析中文 CID 字体乱码
# ✅ 用 PyMuPDF (pymupdf)
import pymupdf
doc = pymupdf.open(pdf_path)
text = "\n".join(page.get_text() for page in doc)
```

### 3. 反斜杠转义陷阱

```python
# ❌ 'E:\WB outputs\data\financials' 显示成 'data inancials'
# ✅ 用 chr(92) 或 r-string
BACKSLASH = chr(92)
text = f'E:{BACKSLASH}WB outputs{BACKSLASH}data{BACKSLASH}financials'
```

完整避坑指南见 [SKILL.md](SKILL.md)。

---

## 📊 已验证案例

### 蒙牛集团数据库 v2.0

| 维度 | 数量 |
|---|---|
| 覆盖公司 | 4 家 (蒙牛+伊利+光明+新乳业) + 6 家控股 |
| PDF 抓取 | 30+ 份 (2021-2025) |
| Obsidian 笔记 | 37 篇 |
| HTML 仪表板 | 3 个 (蒙牛本体+竞品对比+高级分析) |
| 自动化任务 | 工作日 16:10 自动运行 |
| 数据维度 | 13+ (财务/投资/竞品/ESG/研报/控股/海外/供需/估值/营销/...) |

**展示位置**：`E:\WB outputs\mengniu_db\` + Obsidian `蒙牛集团数据库\`

---

## 🎁 适用公司类型

- ✅ A 股大盘股（伊利/茅台/五粮液/海天/比亚迪/宁德时代）
- ✅ 港股（腾讯/美团/京东/百度/小米）
- ✅ 美股（可口可乐/百事/雀巢/沃尔玛/特斯拉）
- ✅ 行业链龙头（光伏/锂电/半导体）
- ✅ 金融机构（招商银行/平安保险）

只需替换 4 项即可套用：股票代码、公司名、财务科目、监管机构。

---

## 🤝 贡献

欢迎贡献：
- 新的数据源接入（Wind/Bloomberg/Choice/iFinD）
- 新的分析维度（AI 预测/情感分析/舆情打分）
- 新的可视化模板（深色/浅色/打印友好）
- 新的公司案例（用本 skill 搭建的数据库）

提交 PR 或 Issue：
- GitHub: https://github.com/gaobin922/gaobin-pages
- Issues: https://github.com/gaobin922/gaobin-pages/issues

---

## 📜 License

[MIT License](LICENSE) — 自由使用、修改、再发布。

引用请注明出处：
```
识君 @ WorkBuddy (https://workbuddy.ai)
来源：https://github.com/gaobin922/gaobin-pages
```

---

## 🌟 Star History

如果本 skill 对你有帮助，欢迎 ⭐ Star 支持开源！

---

## 📚 相关链接

- [WorkBuddy 官网](https://workbuddy.ai)
- [WorkBuddy 文档](https://docs.workbuddy.ai)
- [蒙牛数据库项目展示](https://github.com/gaobin922/gaobin-pages/blob/main/demos/mengniu-db.md)

---

*Built with ❤️ by 识君 @ WorkBuddy · 2026-09-18*
