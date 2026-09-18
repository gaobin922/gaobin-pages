# Plotly HTML 仪表板模板

完整可运行的 Python 脚本，复制后修改数据源即可生成类似蒙牛数据库的交互仪表板。

## 完整模板代码

```python
"""
公司数据库 HTML 仪表板构建器
用法：复制本文件，修改 CONFIG 区域，运行 `python build_html.py`
"""
import json
import plotly.graph_objects as go
from pathlib import Path

# ============== CONFIG ==============
COMPANY_NAME = "XX 公司"
TICKER = "000000.SZ"
DATA_DIR = Path(r'E:\WB outputs\company_db\data')
OUTPUT_PATH = Path(r'E:\WB outputs\company_db\html\dashboard.html')

THEME_COLOR = '#C8102E'  # 公司主题色（蒙牛红）
ACCENT_COLOR = '#3498db'

# ============== 加载数据 ==============
fin = json.load(open(DATA_DIR / 'financials/annual/master.json'))
market = json.load(open(DATA_DIR / 'market/realtime/latest.json'))
competitors = json.load(open(DATA_DIR / 'competitors/financials.json'))

# ============== 图表 1: 营收/净利趋势 ==============
fig1 = go.Figure()
years = [r['year'] for r in fin['annual']]
fig1.add_trace(go.Scatter(x=years, y=[r['revenue'] for r in fin['annual']],
                          mode='lines+markers+text', name='营收 (亿)',
                          text=[f"{r['revenue']:.1f}" for r in fin['annual']],
                          textposition='top center',
                          line=dict(color=THEME_COLOR, width=4),
                          marker=dict(size=14)))
fig1.add_trace(go.Scatter(x=years, y=[r['net_profit'] for r in fin['annual']],
                          mode='lines+markers+text', name='归母净利 (亿)',
                          text=[f"{r['net_profit']:.1f}" for r in fin['annual']],
                          textposition='bottom center',
                          line=dict(color=ACCENT_COLOR, width=4, dash='dash'),
                          marker=dict(size=14, symbol='diamond'),
                          yaxis='y2'))
fig1.update_layout(
    title=f'图1: {COMPANY_NAME} 营收与归母净利 (2021-2025)',
    yaxis_title='营收 (亿)', yaxis2=dict(title='归母净利 (亿)', overlaying='y', side='right'),
    height=400, hovermode='x unified',
)

# ============== 图表 2: 毛利率与净利率 ==============
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=years, y=[r['gross_margin'] for r in fin['annual']],
                     name='毛利率', marker_color=THEME_COLOR,
                     text=[f"{r['gross_margin']:.1f}%" for r in fin['annual']],
                     textposition='outside'))
fig2.add_trace(go.Scatter(x=years, y=[r['roe_weighted'] for r in fin['annual']],
                          mode='lines+markers', name='ROE 加权',
                          line=dict(color=ACCENT_COLOR, width=3),
                          marker=dict(size=12, symbol='diamond')))
fig2.update_layout(title='图2: 盈利能力指标', yaxis_title='%', height=400)

# ============== 图表 3: 4家竞品对比 ==============
fig3 = go.Figure()
for comp in competitors['companies']:
    fig3.add_trace(go.Bar(name=comp['name'],
                           x=['营收', '净利', '毛利率'],
                           y=[comp['revenue'], comp['net_profit'], comp['gross_margin']],
                           text=[f"{comp['revenue']:.0f}", f"{comp['net_profit']:.1f}", f"{comp['gross_margin']:.1f}%"],
                           textposition='outside'))
fig3.update_layout(title='图3: 4家公司核心指标对比', barmode='group', height=400)

# ============== 图表 4: 估值历史 ==============
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=[d['date'] for d in market['history_pe']],
                          y=[d['pe'] for d in market['history_pe']],
                          mode='lines+markers', name='PE TTM',
                          line=dict(color=THEME_COLOR, width=3),
                          marker=dict(size=10)))
fig4.update_layout(title=f'图4: {TICKER} PE 历史', yaxis_title='PE TTM', height=400)

# ============== HTML 组装 ==============
charts_html = ""
for fig, div_id in [(fig1, 'fig1'), (fig2, 'fig2'), (fig3, 'fig3'), (fig4, 'fig4')]:
    charts_html += f"<div class='chart'>{fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)}</div>"

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{COMPANY_NAME} 数据库仪表板</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
       background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
       color: #e6e6e6; padding: 24px; min-height: 100vh; }}
.container {{ max-width: 1400px; margin: 0 auto; }}
header {{ text-align: center; margin-bottom: 32px; padding: 32px;
         background: linear-gradient(90deg, {THEME_COLOR} 0%, #8B0A1F 100%);
         border-radius: 12px; }}
h1 {{ font-size: 36px; margin-bottom: 8px; }}
.kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
            margin-bottom: 32px; }}
.kpi {{ background: rgba(255,255,255,0.05); padding: 24px; border-radius: 12px;
       border-left: 4px solid {THEME_COLOR}; }}
.kpi-value {{ font-size: 32px; font-weight: bold; }}
.kpi-label {{ font-size: 13px; opacity: 0.7; }}
.chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.chart {{ background: rgba(255,255,255,0.03); padding: 20px; border-radius: 12px; }}
.search-box {{ width: 100%; padding: 12px 20px; border-radius: 24px;
              background: rgba(255,255,255,0.05); color: #fff; border: none;
              margin-bottom: 24px; font-size: 14px; }}
.insight {{ background: rgba(200,16,46,0.08); padding: 16px; border-radius: 8px;
           border-left: 3px solid {THEME_COLOR}; margin: 16px 0; }}
</style>
</head>
<body>
<div class="container">
<header>
  <h1>🥛 {COMPANY_NAME} 数据库</h1>
  <div>数据范围 2021-2025 · 主体上市公司 · 更新频率：每日</div>
</header>

<input type="text" class="search-box" placeholder="🔍 搜索..." id="searchBox" onkeyup="filterCharts()">

<div class="kpi-row">
  <div class="kpi"><div class="kpi-label">最新现价</div><div class="kpi-value">{market['price']}</div></div>
  <div class="kpi"><div class="kpi-label">2025 营收 (亿)</div><div class="kpi-value">{fin['annual'][-1]['revenue']:.1f}</div></div>
  <div class="kpi"><div class="kpi-label">2025 净利 (亿)</div><div class="kpi-value">{fin['annual'][-1]['net_profit']:.1f}</div></div>
  <div class="kpi"><div class="kpi-label">2025 毛利率</div><div class="kpi-value">{fin['annual'][-1]['gross_margin']:.1f}%</div></div>
</div>

<div class="chart-grid">
  {charts_html}
</div>

<div class="insight">
  💡 <b>关键洞察：</b>...（此处填入你的战略洞察）
</div>

</div>

<script>
function filterCharts() {{
  const query = document.getElementById('searchBox').value.toLowerCase();
  document.querySelectorAll('.chart, .kpi').forEach(el => {{
    el.style.display = el.textContent.toLowerCase().includes(query) ? '' : 'none';
  }});
}}
</script>
</body>
</html>
"""

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(html, encoding='utf-8')
print(f"✅ 仪表板已生成: {OUTPUT_PATH}")
print(f"   文件大小: {len(html) // 1024} KB")
```

---

## 自定义要点

1. **数据源路径**: 修改 `DATA_DIR`
2. **公司主题色**: 修改 `THEME_COLOR`（CSS 变量风格全文档生效）
3. **图表数量**: 复制图表 1-4 模板，加更多图表（推荐 6-10 个）
4. **KPI 卡片**: 根据需要添加/删除
5. **洞察文本**: 在 `.insight` 块中填入文字

---

## 进阶图表模板

### 4家竞品市占率对比（堆叠柱）
```python
fig_share = go.Figure()
for comp in competitors['companies']:
    fig_share.add_trace(go.Bar(
        x=['液态奶', '奶粉', '冰激凌', '奶酪'],
        y=[comp['share_liquid'], comp['share_formula'], comp['share_icecream'], comp['share_cheese']],
        name=comp['name'],
    ))
fig_share.update_layout(barmode='stack', title='图N: 各品类市占率对比', height=400)
```

### 雷达图（多维度能力对比）
```python
import plotly.graph_objects as go

categories = ['营收规模', '净利率', 'ROE', '海外占比', '研发投入', '品牌力']
fig_radar = go.Figure()
for comp in competitors['companies']:
    fig_radar.add_trace(go.Scatterpolar(
        r=[comp['revenue_score'], comp['margin_score'], comp['roe_score'],
           comp['overseas_score'], comp['rd_score'], comp['brand_score']],
        theta=categories, fill='toself', name=comp['name'],
    ))
fig_radar.update_layout(title='图N: 多维度能力雷达图', height=500)
```

### 估值散点图（PE vs ROE）
```python
fig_scatter = go.Figure()
for comp in competitors['companies']:
    fig_scatter.add_trace(go.Scatter(
        x=[comp['pe']], y=[comp['roe']],
        mode='markers+text', text=[comp['name']],
        textposition='top center',
        marker=dict(size=comp['mcap']/100, color=comp['color']),
    ))
fig_scatter.update_layout(title='图N: PE vs ROE 估值', xaxis_title='PE', yaxis_title='ROE %')
```
