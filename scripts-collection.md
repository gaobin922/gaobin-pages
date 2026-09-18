# 数据抓取脚本集合 — Database Builder Skill

本文档汇总所有可复用的 Python 抓取脚本片段。复制后根据目标公司股票代码调整即可使用。

---

## 1. cninfo 公告抓取（A股专用）

```python
"""抓取 A 股公司近 N 年的所有年报+中报 PDF 直链"""
import requests
import json
import re
from pathlib import Path

def search_cninfo_reports(stock_code: str, org_id: str, start_date: str, end_date: str,
                          report_types: list = ['annual', '1H', '1Q', '3Q']) -> list:
    """从 cninfo 巨潮资讯网搜索指定公司的公告 PDF"""
    url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'

    # 类型映射
    type_map = {
        'annual': 'category_ndbg_szsh',
        '1H': 'category_bndbg_szsh',
        '1Q': 'category_yjdbg_szsh',
        '3Q': 'category_sjdbg_szsh',
    }
    category = ','.join(type_map[t] for t in report_types if t in type_map)

    results = []
    for page in range(1, 6):  # 最多 5 页
        data = {
            'stock': f'{stock_code},{org_id}',
            'tabName': 'fulltext',
            'pageSize': 50,
            'pageNum': page,
            'column': 'sse' if stock_code.startswith('6') else 'szse',
            'plate': 'sse' if stock_code.startswith('6') else 'szse',
            'category': category,
            'seDate': start_date + '~' + end_date,
            'isHLtitle': 'true',
        }
        resp = requests.post(url, data=data, headers={
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://www.cninfo.com.cn',
            'Referer': 'http://www.cninfo.com.cn/'
        }, timeout=30)
        items = resp.json().get('announcements') or []
        for item in items:
            title = item['announcementTitle']
            # 过滤业绩说明会、临时公告等
            if re.search(r'(业绩说明会|临时|临时公告|关于召开)', title):
                continue
            # 确认是真实报告
            if any(kw in title for kw in ['年度报告', '半年度报告', '第一季度报告', '第三季度报告']):
                results.append({
                    'title': title,
                    'pdf_url': 'http://static.cninfo.com.cn/' + item['adjunctUrl'],
                    'announcement_id': item['announcementId'],
                    'date': item['announcementTime'],
                })
    return results


def get_org_id(stock_code: str) -> str:
    """根据股票代码获取 cninfo orgId"""
    url = 'http://www.cninfo.com.cn/new/information/topSearch/detailOfQuery'
    resp = requests.post(url, data={'keyWord': stock_code, 'maxNum': 10},
                         headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    return resp.json()['keyBoardList'][0]['orgId']


def batch_download_pdfs(reports: list, output_dir: str):
    """批量下载 PDF"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for r in reports:
        # 简化文件名
        safe_title = re.sub(r'[^\w\u4e00-\u9fff]+', '_', r['title'])[:80]
        filename = f"{safe_title}.pdf"
        filepath = Path(output_dir) / filename
        if filepath.exists():
            print(f"已存在: {filename}")
            continue
        try:
            resp = requests.get(r['pdf_url'], timeout=60)
            filepath.write_bytes(resp.content)
            print(f"✅ {filename} ({len(resp.content)//1024}KB)")
        except Exception as e:
            print(f"❌ {filename}: {e}")


if __name__ == '__main__':
    # 示例：伊利股份
    code = '600887'
    org = get_org_id(code)
    print(f"orgId: {org}")

    reports = search_cninfo_reports(code, org, '2022-01-01', '2026-09-18',
                                     report_types=['annual', '1H'])
    print(f"找到 {len(reports)} 个报告")

    batch_download_pdfs(reports, r'E:\WB outputs\company_db\pdf\annual')
```

---

## 2. PyMuPDF 解析 + 字段提取

```python
"""使用 PyMuPDF 解析中文 PDF 并提取关键财务字段"""
import pymupdf
import re
from pathlib import Path

def extract_pdf_text(pdf_path: str) -> str:
    """PyMuPDF 提取全文（中文安全）"""
    doc = pymupdf.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def extract_financial_fields(text: str) -> dict:
    """从业绩公告文本中提取关键财务字段"""
    result = {
        'revenue': None, 'net_profit': None, 'gross_margin': None,
        'eps_basic': None, 'roe_weighted': None,
        'total_assets': None, 'equity_attr': None,
    }

    # 营业收入（亿元）
    patterns = [
        # 2025 风格（百万元）
        (r'营业(?:收入|总收入)[^0-9]{0,30}?([\d,]+(?:\.\d+)?)\s*(?:百万元|千元)?',
         'revenue', 0.0001),  # 百万元 → 亿元
        # 2024 风格（元）
        (r'营业(?:收入|总收入)[^0-9]{0,30}?([\d,]+(?:\.\d+)?)\s*元',
         'revenue', 0.00000001),
    ]
    for pat, field, scale in patterns:
        m = re.search(pat, text)
        if m:
            try:
                result[field] = float(m.group(1).replace(',', '')) * scale
                break
            except: pass

    # 归母净利润
    m = re.search(r'归[属于属]\s*(?:于)?(?:本公司|上市公司)股东(?:的)?(?:应占)?\s*(?:亏损)?(?:净[利利润]+)?[^0-9]{0,30}?([\d,]+(?:\.\d+)?)',
                   text)
    if m:
        try:
            result['net_profit'] = float(m.group(1).replace(',', '')) * 0.0001  # 百万元 → 亿元
        except: pass

    # 毛利率
    m = re.search(r'毛[利]率[^0-9]{0,10}?([\d.]+)\s*[%％]', text)
    if m:
        result['gross_margin'] = float(m.group(1))

    # EPS
    m = re.search(r'基本每股(?:收益|亏損)[^0-9]{0,10}?([\d.]+)', text)
    if m:
        result['eps_basic'] = float(m.group(1))

    # ROE
    m = re.search(r'加权平均[^\n]{0,5}?(?:净资产)?收益率[^0-9]{0,10}?([\d.]+)\s*[%％]', text)
    if m:
        result['roe_weighted'] = float(m.group(1))

    return result


# 测试
if __name__ == '__main__':
    pdf = r'E:\WB outputs\mengniu_db\pdf\announcement\2025_annual_results.pdf'
    text = extract_pdf_text(pdf)
    fields = extract_financial_fields(text)
    print(json.dumps(fields, ensure_ascii=False, indent=2))
```

---

## 3. 行情抓取（A 股 + 港股）

```python
"""港股 + A 股实时行情抓取"""
import requests
import re
import json

def get_hk_quote(stock_code: str) -> dict:
    """港股实时行情（新浪财经）"""
    url = f'https://hq.sinajs.cn/list=hk{stock_code}'
    resp = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn/'}, timeout=30)
    text = resp.text
    # var hk02319="腾讯控股,01810,300.000,..."
    m = re.match(r'var hk\d+="([^"]+)"', text)
    if not m: return {}
    fields = m.group(1).split(',')
    if len(fields) < 6: return {}
    return {
        'name': fields[0],
        'code': stock_code,
        'price': float(fields[6] or 0),
        'prev_close': float(fields[3] or 0),
        'open': float(fields[5] or 0),
        'volume': int(float(fields[12] or 0)),
    }


def get_a_quote(stock_code: str) -> dict:
    """A 股实时行情（东方财富）"""
    # secid: 沪市 1.600xxx，深市 0.002xxx
    secid = f'1.{stock_code}' if stock_code.startswith('6') else f'0.{stock_code}'
    url = 'https://push2.eastmoney.com/api/qt/stock/get'
    params = {
        'secid': secid,
        'fields': 'f43,f44,f45,f46,f47,f48,f57,f58,f60,f169,f170',
        # f43=最新价 f44=最高 f45=最低 f46=今开 f47=成交量 f48=成交额
        # f57=代码 f58=名称 f60=昨收 f169=涨跌额 f170=涨跌幅
    }
    resp = requests.get(url, params=params, timeout=30)
    d = resp.json().get('data', {})
    return {
        'code': stock_code,
        'name': d.get('f58'),
        'price': d.get('f43') / 100,
        'change': d.get('f169') / 100,
        'change_pct': d.get('f170') / 100,
        'open': d.get('f46') / 100,
        'high': d.get('f44') / 100,
        'low': d.get('f45') / 100,
        'volume': d.get('f47'),
    }


if __name__ == '__main__':
    print("蒙牛:", get_hk_quote('02319'))
    print("伊利:", get_a_quote('600887'))
    print("新乳业:", get_a_quote('002946'))
```

---

## 4. 行业/原奶价格抓取（农业农村部）

```python
"""从农业农村部《农产品供需形势分析月报》抓取生鲜乳价格"""
import requests
from bs4 import BeautifulSoup
import re

def fetch_milk_price_history() -> list:
    """爬取历史月度原奶价"""
    # 农业农村部 PDF 直链（按月）
    base_urls = [
        ('https://www.agri.cn/sj/jcyj/202405/P020240522359850839637.pdf', '2024-04'),
        ('https://www.agri.cn/sj/jcyj/202311/P020231130385417738061.pdf', '2023-11'),
        # 按需添加更多
    ]

    results = []
    for url, period in base_urls:
        try:
            resp = requests.get(url, timeout=30)
            import pymupdf
            doc = pymupdf.open(stream=resp.content, filetype='pdf')
            text = "\n".join(page.get_text() for page in doc)
            doc.close()

            # 解析价格表
            # 格式: | 2024/02 | 3.63 | ...
            pattern = r'(\d{4})/(\d{2})\s*\|?\s*([\d.]+)'
            for m in re.finditer(pattern, text):
                year, month, price = m.groups()
                results.append({
                    'year': int(year),
                    'month': int(month),
                    'price': float(price),
                    'source': f'农业农村部 {period}',
                })
        except Exception as e:
            print(f"❌ {period}: {e}")

    return results
```

---

## 5. HTML 仪表板构建

参考 `templates/dashboard-template.py`，核心结构：

```python
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json

# 加载数据
fin = json.load(open(r'E:\WB outputs\company_db\data\financials\annual\master.json'))

# 创建图表
fig1 = go.Figure(go.Scatter(
    x=[r['year'] for r in fin['annual']],
    y=[r['revenue'] for r in fin['annual']],
    mode='lines+markers+text',
    text=[f"{r['revenue']:.1f}" for r in fin['annual']],
    textposition='top center',
    line=dict(color='#C8102E', width=4),
))
fig1.update_layout(title='营收趋势 (2021-2025)', height=400)

# 生成 HTML
html = f"""
<!DOCTYPE html><html>...
{plotly_div}
...</html>
"""
Path(r'E:\WB outputs\company_db\html\dashboard.html').write_text(html)
```

---

## 6. Obsidian 笔记自动生成

```python
"""根据 JSON 数据自动生成 Obsidian 笔记"""
import json
from pathlib import Path
import datetime

def build_obsidian_note(data: dict, title: str, note_type: str, tags: list,
                         source_path: str, output_dir: str) -> str:
    today = datetime.date.today().isoformat()
    note_path = Path(output_dir) / f"{title}.md"

    md = f"""---
title: {title}
type: {note_type}
tags: {tags}
created: {today}
updated: {today}
source: {source_path}
---

# {title}

## 核心数据表

| 指标 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
"""
    # ... 根据 data 动态生成表格
    md += """

## 关键洞察

- 洞察1...
- 洞察2...
- 洞察3...

## 相关文档
- [[其他笔记]]

## 更新记录
- """ + today + ": v1.0 建立"
    note_path.write_text(md, encoding='utf-8')
    return str(note_path)
```

---

## 7. 每日更新脚本框架

```python
"""每日自动化更新入口脚本"""
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def daily_update():
    """主流程"""
    today = datetime.now().strftime('%Y-%m-%d')

    # 1. 抓数据（调用前述抓取脚本）
    print("Step 1: 抓取实时行情...")
    subprocess.run(['python', 'scripts/fetch_quotes.py'], check=False)

    print("Step 2: 抓取新公告...")
    subprocess.run(['python', 'scripts/fetch_announcements.py'], check=False)

    # 2. 解析 PDF（如果有新发布）
    print("Step 3: 解析新 PDF...")
    subprocess.run(['python', 'scripts/parse_new_pdfs.py'], check=False)

    # 3. 重建 HTML
    print("Step 4: 重建 HTML 仪表板...")
    subprocess.run(['python', 'scripts/build_html.py'], check=False)

    # 4. 更新 Obsidian
    print("Step 5: 更新 Obsidian 笔记...")
    subprocess.run(['python', 'scripts/build_obsidian.py'], check=False)

    # 5. 更新 Daily Note
    print(f"Step 6: 生成 {today} Daily Note...")
    build_daily_note(today)

    print("✅ 全部完成")


if __name__ == '__main__':
    daily_update()
```
