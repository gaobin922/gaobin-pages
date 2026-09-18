# Obsidian 笔记模板

每篇数据库笔记使用以下 frontmatter + 结构。复制后根据数据填充。

---

## Frontmatter（必填）

```yaml
---
title: {公司} {维度}
type: {snapshot | annual_report | comparison | profile | daily_update | esg-analysis | research-sentiment | holdings-network | overseas-business | industry-supply-demand | valuation-analysis | marketing-expenses}
tags: [{公司}, {维度1}, {维度2}]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: E:\WB outputs\{公司}_db\data\{路径}\{文件}.json
---
```

**type 枚举**：
- `snapshot` — KPI 快照
- `annual_report` — 年度报告分析
- `comparison` — 多家公司对比
- `profile` — 公司画像
- `daily_update` — 每日自动化快照
- `esg-analysis` — ESG 分析
- `research-sentiment` — 研报情绪
- `holdings-network` — 控股网络
- `overseas-business` — 海外业务
- `industry-supply-demand` — 行业供需
- `valuation-analysis` — 估值分析
- `marketing-expenses` — 营销费用

---

## 笔记主体结构（5 个必填板块）

### 1. 数据来源（透明可溯）

```markdown
## 数据来源
- {PDF 来源} · 链接
- {网页来源} · 链接
- {API 来源} · 链接
- 关键引用：`{具体出处}`
```

### 2. 核心数据表（最少 1 张 5 年/多年表）

```markdown
## 5 年关键数据

| 年份 | 营收 (亿) | 归母净利 (亿) | 毛利率 | 净利率 | ROE | EPS |
|---|---|---|---|---|---|---|
| 2021 | ... | ... | ... | ... | ... | ... |
| 2022 | ... | ... | ... | ... | ... | ... |
| 2023 | ... | ... | ... | ... | ... | ... |
| 2024 | ... | ... | ... | ... | ... | ... |
| 2025 | ... | ... | ... | ... | ... | ... |
```

**表格规则**：
- 数字统一保留 1-2 位小数
- 百分比带 `%`
- 缺失值用 `-` 而非 0
- 表格前后空行

### 3. 战略洞察（3-5 个 bullet point）

```markdown
## 关键洞察

- 📈 **增长维度**: 2025 营收 +X% YoY，驱动力是...
- ⚠️ **风险维度**: 2024 净利暴跌主因是...
- 🎯 **战略维度**: 公司"一体化两翼"战略中，海外是...
- 💡 **机会维度**: 奶价反弹将利好...
```

### 4. 相关文档链接（最少 3 个 wikilink）

```markdown
## 🔗 相关文档
- [[蒙牛集团数据库|MOC 主入口]]
- [[财务/年报/master_summary|年度财务汇总]]
- [[竞品分析/4家公司财务对比|4家对比]]
- [数据源 JSON](E:\\WB outputs\\mengniu_db\\v2\\{文件}.json)
```

### 5. 更新记录

```markdown
## 📅 更新记录
- 2026-09-15: v1.0 建立
- 2026-09-16: v1.1 修正...
- 2026-09-18: v2.0 加入 7 个高级维度
```

---

## 高级写法（可选）

### Dataview 查询（让笔记自动索引）

```markdown
\`\`\`dataview
TABLE WITHOUT ID
  file.link AS "报告",
  year AS "年份",
  revenue AS "营收",
  np_attr_owners AS "归母净利",
  updated AS "更新"
FROM "蒙牛集团数据库/财务/年度"
WHERE type = "annual_report"
SORT year DESC
\`\`\`
```

### Callout 强调（视觉效果）

```markdown
> [!important] 关键洞察
> 蒙牛 2024 净利 1.04 亿，受贝拉米 39.8 亿减值拖累。
> 排除减值后实际利润 44 亿，派息率 45%。

> [!warning] 风险提示
> 海外占比仅 5.5%，"国际化"叙事兑现慢。

> [!tip] 投资建议
> Forward PE 11.73x 显示估值修复空间巨大。
```

### Mermaid 图（控股网络 / 业务结构）

```markdown
\`\`\`mermaid
graph TD
    蒙牛02319 -->|56.36%| 现代牧业1117
    蒙牛02319 -->|53.51%| 艾雪Aice
    蒙牛02319 -->|100%| 贝拉米
    蒙牛02319 -->|32.99%| 妙可蓝多
    蒙牛02319 -->|23.34%| 中国圣牧
\`\`\`
```

### 嵌入 Plotly 图（HTML 截图）

将 plotly 图导出为 PNG 后用 `![[图.png]]` 嵌入，或用 iframe：

```markdown
<iframe src="file:///E:/WB outputs/mengniu_db/html/v2_dashboard.html"
        width="100%" height="600" frameborder="0"></iframe>
```

---

## 命名规范

| 类型 | 命名 |
|---|---|
| MOC 主入口 | `{公司}集团数据库.md` |
| 年度报告 | `{年份}年报.md` |
| MOC 子模块 | `竞品分析.md` / `ESG.md` |
| 维度分析 | `{维度} {细分}.md`，如 `估值历史与同业对比.md` |
| Daily Note | `Daily Updates/{YYYY-MM-DD}.md` |
| 工作流 | `工作流Prompt词.md` |

---

## 反模式（避免）

❌ **空表格占位符**: `| - | - | - |` 必须替换为真实数据
❌ **路径损坏**: `data inancials`（`\f` 被吞）必须用 chr(92) 修复
❌ **断链 wikilink**: `[[不存在的笔记]]` 必须指向真实文件
❌ **过度嵌套 f-string**: 拆变量或用 concat
❌ **缺失 frontmatter**: Dataview 不会索引
❌ **跨模块绝对路径**: 优先用 `[[wikilink]]` 而非 `E:\WB outputs\...`
