---
name: db-builder-shiijun
description: This skill should be used when the user asks to build a structured financial/investment database for any A-share/HK/US-listed company — including financial data scraping (annual reports, interim reports, announcements), market data, competitive analysis, ESG ratings, sell-side research, supply/demand, holdings network, valuation history, marketing analysis, automated Obsidian notes, interactive HTML dashboards, and scheduled automation. It triggers on requests like "帮我搭建XX公司数据库", "抓取XX年报数据", "做一份可视化财务仪表板", "把XX数据库加入Obsidian", "每日自动更新XX数据". Built and battle-tested on 蒙牛集团 (02319.HK) project with 4 competitors + 6 holdings + 9+ data dimensions.
license: MIT
agent_created: true
allowed-tools:
  - WebFetch
  - WebSearch
  - Bash
  - Write
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - Skill
---

# 数据库搭建工作流 (识君版) — DB Builder Shiijun

为任意上市公司搭建一套完整的"数据抓取 → 结构化存储 → 可视化展示 → 知识库沉淀 → 自动化更新"端到端工作流。已在蒙牛集团 (02319.HK) 项目上验证：抓取 4 家公司 5 年 26 份 PDF + 7 个高级分析维度 + 37 篇 Obsidian 笔记 + 3 个 HTML 仪表板 + 工作日自动更新。

---

## When to use this skill

触发条件（任一即可）：
- 用户说 "帮我搭建XX公司数据库" / "构建XX财务数据库"
- 用户说 "抓取XX公司年报/中报/季报"
- 用户说 "做一份XX财务仪表板/可视化"
- 用户说 "把XX数据加入Obsidian/Notion/飞书"
- 用户说 "每日自动更新XX数据"
- 用户说 "我想长期跟踪XX公司"
- 用户说 "分析XX与YY的竞争"

不适用于：
- 简单单次查询（用普通 WebSearch）
- 已经成型的数据库维护（直接用其专属 skill）
- 加密货币/私募/非公开数据源

---

## 工作流总览（12 阶段）

### Stage 0 — 启动问询（必做，不能跳过）

启动任何数据库项目前，**必须** 用 AskUserQuestion 一次性问完 4 个关键决策：

```
1. 数据维度优先级（多选）：
   - 财务面（核心）| 投资端 | 消费者端 | 生产端 | 营销新品 | 舆情公告

2. 是否包含关联方/控股子公司：
   - 仅上市公司主体 | 主体+控股子公司

3. 历史跨度：
   - 近 5 年（2021-2025）| 近 10 年 | 上市以来全部

4. Obsidian/Notion 集成方式：
   - 新建独立目录 | 嵌入 Daily Note | 独立目录+Daily Note 摘要
```

### Stage 1 — 加载核心技能

并行调用：
- `cn-financial-scraper`（中国金融机构数据爬取：A股/港股/公告/舆情）
- `data-visualization`（plotly/seaborn/matplotlib 图表）
- `obsidian__skillhub`（Obsidian 知识库管理）

如果项目是港股，需额外 WebSearch 港交所披露易入口。

### Stage 2 — 目录结构约定

```
E:\WB outputs\{公司名}_db\
├── pdf/
│   ├── announcement/        # 业绩公告
│   └── presentation/        # 业绩 PPT
├── text/                    # PDF→txt 解析结果
├── data/
│   ├── financials/annual/   # 年度财务（CSV + JSON）
│   ├── financials/interim/  # 中期财务
│   ├── market/realtime/     # 实时行情
│   ├── market/price/        # 历史价格
│   ├── competitors/         # 竞品对比数据
│   └── v2/                  # 高级分析维度（ESG/研报/控股等）
├── html/                    # plotly 仪表板
├── reports/                  # 原始年报txt
└── logs/                     # 自动化日志

E:\WB-Obsidian\WB-Obsidian\{公司名}集团数据库\
├── {公司名}集团数据库.md     # MOC 主入口
├── 财务/年报/                # 各年报笔记 + master_summary
├── 投资端/                   # 股价、估值、研报
├── 消费者端/
├── 生产端/
├── 营销与新品/
├── 舆情与公告/
├── ESG/                      # v2.0 新增
├── 控股参股/                # v2.0 新增
├── 海外业务/                # v2.0 新增
├── 行业/                     # v2.0 新增
├── 竞品分析/
├── Daily Updates/            # 每日自动化快照
└── 工作流Prompt词.md        # 完整工作流文档
```

### Stage 3 — 财务数据抓取（v1.0 核心）

#### 3.1 PDF 下载
- **港股**: 用 `https://www1.hkexnews.hk/listedco/listconews/sehk/YYYY/MMDD/ID.pdf` 直链
- **A股**: 通过 cninfo 巨潮资讯网 API
- **公司IR**: 如蒙牛 `https://mengniuir.com/pdf/presentation/YYYYar_ppt_{tc|en}.pdf`
- **批量下载脚本模板**: 见 `references/scripts-collection.md`

#### 3.2 PDF 解析
**强制使用 PyMuPDF**（pypdf 中文乱码）：
```python
import pymupdf  # 新版，fitz 已废弃
doc = pymupdf.open(pdf_path)
text = "\n".join(page.get_text() for page in doc)
```

#### 3.3 关键字段提取
从业绩公告/年报自动提取：
- 营收 / 归母净利 / 毛利率 / 净利率
- EPS（基本 + 摊薄）/ ROE 加权
- 总资产 / 总负债 / 经营现金流
- 分业务收入（液态奶 / 冰激凌 / 奶粉 / 奶酪 等）


### Stage 4 — 行情数据抓取

#### 港股实时行情
```python
import requests
url = 'https://hq.sinajs.cn/list=hk02319'
resp = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn/'})
# 解析: var hk02319="腾讯控股,01810,300.000,..."
```

#### A股实时行情
```python
url = 'https://push2.eastmoney.com/api/qt/stock/get'
params = {'secid': '1.600887', 'fields': 'f43,f44,f45,f46,f60,f170'}  # 沪市
# 深市: '0.002946'
```

#### 历史 K 线（兜底）
- 东财 push2his（经常风控）
- 雪球 stock.xueqiu.com/v5/stock/chart/kline

### Stage 5 — 行业/市占率抓取

数据源优先级：
1. **欧睿国际 (Euromonitor)** — 液态奶 / 整体乳制品
2. **弗若斯特沙利文** — 细分品类
3. **灼识咨询** — 综合规模
4. **中国奶业协会 / 国家奶牛产业技术体系** — 中国特色

搜索词模板：`"XX行业" 市占率 "2024" 欧睿 沙利文`

### Stage 6 — 控股/参股公司数据（v2.0）

```
抓取控股关系 → 列出 3-5 家核心子公司 → 逐家抓取年报
├─ A股子公司: cninfo
├─ 港股子公司: 港交所披露易
├─ 美股子公司: SEC EDGAR (10-K/10-Q)
└─ 未上市子公司: 母公司年报"主要附属公司"章节
```

### Stage 7 — ESG 数据（v2.0）

抓取 3 个核心评级：
- **MSCI ESG**: web search `"XX" MSCI ESG 评级 2025`
- **恒生 ESG**: web search `"XX" 恒生 ESG 50`
- **标普 CSA**: web search `"XX" 标普可持续发展年鉴`

环境指标：碳排放强度（kgCO2e/吨）、绿色工厂数、节水节电

### Stage 8 — 券商研报（v2.0）

数据源：
1. **广发证券 MCP**（如已连接）
2. **AAStocks** (aastocks.com) — 香港研报聚合
3. **新浪财经 / 同花顺 / 东方财富** — 研报中心
4. **公司投资者关系页面**

抓取字段：日期、机构、分析师、标题、评级、目标价、核心观点

### Stage 9 — HTML 仪表板构建

**强制要求**：
- 使用 plotly（不要 matplotlib 静态图）
- 4-8 个 KPI 卡片顶部
- 至少 6-10 个交互图（趋势/对比/份额/价格/比率）
- 搜索框（field filter）+ 字段高亮
- 每图下方配 1-2 段战略洞察（带颜色边框）
- 深色主题（适合展示）+ 顶部蒙牛/公司主题色

参考模板：`templates/dashboard-template.py`

### Stage 10 — Obsidian 笔记构建

每篇笔记 frontmatter 必填：
```yaml
---
title: 笔记标题
type: 笔记类型 (analysis/comparison/profile/snapshot/daily_update)
tags: [标签1, 标签2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: 数据源 JSON 路径
---
```

每篇笔记必须包含：
1. **5 年关键数据表**（或多年趋势表）
2. **战略洞察**（3-5 个 bullet point）
3. **关键洞察**（用 ```dataview 或 callout 块）
4. **相关文档链接**（`[[wikilink]]` 至少 3 个）
5. **数据源链接**（指向 JSON/CSV 文件）
6. **更新记录**

参考模板：`references/obsidian-template.md`

### Stage 11 — 自动化配置

使用 `automation_update` 工具创建工作日定时任务：

```
scheduleType: recurring
rrule: FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=16;BYMINUTE=10
```

prompt 应包含：
- 抓取清单（行情/公告/舆情/行业/PDF）
- 重建脚本（HTML + Obsidian）
- 容错（单源失败不阻塞 + 重试 3 次 + 错误日志）
- 完成后调用 `present_files`

### Stage 12 — 编写工作流 Prompt 词

完成所有抓取后，**必须**编写完整的可复用 prompt 词：
- Obsidian 端：`{公司名}集团数据库/工作流Prompt词.md`
- WB outputs 端：`E:\WB outputs\资料库\{公司}数据库工作流prompt词.md`

双写目的：Obsidian 用于个人复用，WB outputs 用于跨项目复用。

---

## 关键技术清单（避坑指南）

### 1. cninfo API 正确姿势（最易踩坑）

```python
# ❌ 错误：用 'stock=orgId,code' 或 'searchkey=年度报告' → 找不到
# ✅ 正确：用 secid + stock 组合

import requests
url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'

# 第1步：先拿 orgId
r1 = requests.post(
    'http://www.cninfo.com.cn/new/information/topSearch/detailOfQuery',
    data={'keyWord': '600887', 'maxNum': 10},
    headers={'User-Agent': 'Mozilla/5.0'}
)
org_id = r1.json()['keyBoardList'][0]['orgId']  # gssh0600887

# 第2步：拉公告列表（必须传 secid + stock）
data = {
    'stock': f'600887,{org_id}',
    'tabName': 'fulltext',
    'pageSize': 50,
    'pageNum': 1,
    'column': 'sse',  # 上交所
    'plate': 'sse',
    'category': '',
    'seDate': '2025-04-01~2025-05-30',
}
r2 = requests.post(url, data=data, headers={
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/x-www-form-urlencoded'
})
items = r2.json()['announcements']
```

### 2. PDF 中文解析

```python
# ❌ pypdf 解析中文 CID 字体乱码
# ✅ 用 PyMuPDF (fitz)
import pymupdf  # 新版，fitz 已废弃
doc = pymupdf.open(pdf_path)
text = "\n".join(page.get_text() for page in doc)
```

### 3. 反斜杠转义陷阱

```python
# ❌ Python 字符串里 \f 被解释成 form feed (\x0c)
text = 'E:\WB outputs\data\financials'  # 显示成 "data inancials"

# ✅ 用 chr(92) 或 r-string
BACKSLASH = chr(92)
text = f'E:{BACKSLASH}WB outputs{BACKSLASH}data{BACKSLASH}financials'
# 或
text = r'E:\WB outputs\data\financials'
```

### 4. 修复已写入文件的 \x0c/\x07 控制字符

```python
# 写入后才发现 \f 变 \x0c \a 变 \x07
from pathlib import Path
p = Path(r'E:\WB-Obsidian\WB-Obsidian\蒙牛集团数据库\财务\年度\master_summary.md')
raw = p.read_bytes()
raw = raw.replace(b'\x0c', b'\\f').replace(b'\x07', b'\\a')
p.write_bytes(raw)
```

### 5. AskUserQuestion 一次性问完

```
# ✅ 正确：一次性 4 个 question 字段
# ❌ 错误：分 4 次单独调用，会卡住 workflow
```

### 6. plotly CDN 减小 HTML 大小

```html
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
# 不要用本地 plotly.js（500KB+），用 CDN
```

### 7. f-string 嵌套花括号

```python
# ❌ 错误：f-string 内嵌 f-string
text = f"... {f'value: {x}'} ..."

# ✅ 正确：拆变量
val_str = f"value: {x}"
text = f"... {val_str} ..."
```

---

## 质量检查清单（每个数据库必过）

- [ ] 5 年财务完整（营收/净利/毛利率/EPS/ROE/资产负债）
- [ ] 4-5 年 PDF 已下载并 PyMuPDF 解析
- [ ] 实时行情能成功抓取（至少 1 个数据源可用）
- [ ] 行业市占率有 2-3 个独立来源
- [ ] 控股子公司至少覆盖 3-5 家核心
- [ ] HTML 仪表板有搜索 + KPI + 至少 6 个交互图
- [ ] Obsidian 至少 8 篇笔记 + 1 个 MOC
- [ ] 每日自动化已配置且能成功运行 1 次
- [ ] 工作流 prompt 词已写入 Obsidian + WB outputs
- [ ] 路径全部使用正斜杠/或正确转义的反斜杠
- [ ] 占位符 `-` 全部填入真实数据
- [ ] cross-link `[[wikilink]]` 全部链接到真实存在的笔记
- [ ] frontmatter 必填字段完整（title/type/tags/created/updated/source）

---

## 适用公司类型

本工作流可直接套用于：
- ✅ **A 股大盘股**：伊利、茅台、五粮液、海天、比亚迪、宁德时代
- ✅ **港股**：腾讯、美团、京东、百度、小米
- ✅ **美股**：可口可乐、百事、雀巢、沃尔玛、特斯拉
- ✅ **行业链**：光伏/锂电/半导体龙头
- ✅ **金融机构**：招商银行、平安保险

只需替换：
1. 股票代码 + 公司名
2. 财务科目（金融/保险 vs 食品有差异）
3. 监管机构（A股 cninfo / 港股 港交所 / 美股 SEC EDGAR）

---

## 完整工作流文档

12 阶段详细规范 + 已验证案例见：
- `templates/dashboard-template.py`
- `references/obsidian-template.md`
- `references/scripts-collection.md`

---

## 工作流总时长

| 阶段 | 时长参考 |
|---|---|
| 0. 问询 | 2 分钟 |
| 1. 加载技能 | 1 分钟 |
| 2. 目录规划 | 1 分钟 |
| 3. 财务抓取 | 30 分钟 |
| 4. 行情抓取 | 15 分钟 |
| 5. 行业抓取 | 20 分钟 |
| 6. 控股抓取 | 20 分钟 |
| 7. ESG 抓取 | 15 分钟 |
| 8. 研报抓取 | 15 分钟 |
| 9. HTML 仪表板 | 30 分钟 |
| 10. Obsidian 笔记 | 30 分钟 |
| 11. 自动化配置 | 5 分钟 |
| 12. Prompt 词编写 | 30 分钟 |
| **合计** | **3-4 小时** |

---

## 版本历史

- **v1.0** (2026-09-15) — 蒙牛数据库初版（财务+竞品，37 篇笔记，3 个 HTML）
- **v1.1** (2026-09-16) — 加入伊利/光明/新乳业 4 家竞品 + 9 篇竞品笔记
- **v2.0** (2026-09-18) — 新增 7 个高级分析维度（ESG/研报/控股/海外/供需/估值/营销）
- **v2.1** (2026-09-18) — 抽出本 SKILL，全网开源

---

## License

MIT — 自由使用、修改、再发布。引用请注明出处：识君 @ WorkBuddy / https://github.com/gaobin922/gaobin-pages
