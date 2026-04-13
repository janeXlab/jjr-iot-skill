#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""嘉宝果生长环境数据可视化报告 v2 - 带植物照片"""

import json
import os
from datetime import datetime
from collections import defaultdict

# 嘉宝果适宜条件
OPTIMAL_TEMP_MIN = 20
OPTIMAL_TEMP_MAX = 30

# 读取数据
print("📊 读取温度数据...")
with open('/tmp/temp_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

temp_raw = raw_data.get('result', [])
print(f"✅ 获取 {len(temp_raw)} 条温度数据")

# 解析数据
temp_data = []
for item in temp_raw:
    try:
        temp_data.append({
            'time': datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S'),
            'value': float(item['value'])
        })
    except:
        continue

# 计算统计
values = [d['value'] for d in temp_data]
stats = {
    'count': len(values),
    'max': max(values),
    'min': min(values),
    'avg': sum(values) / len(values)
}

# 按日统计
daily = defaultdict(list)
for d in temp_data:
    date = d['time'].strftime('%Y-%m-%d')
    daily[date].append(d['value'])

daily_stats = {}
for date, vals in sorted(daily.items()):
    daily_stats[date] = {'max': max(vals), 'min': min(vals), 'avg': sum(vals)/len(vals)}

# 适宜度分析
total = len(temp_data)
optimal = sum(1 for d in temp_data if OPTIMAL_TEMP_MIN <= d['value'] <= OPTIMAL_TEMP_MAX)
hot = sum(1 for d in temp_data if d['value'] > OPTIMAL_TEMP_MAX)
cold = sum(1 for d in temp_data if d['value'] < OPTIMAL_TEMP_MIN)

comfort = {
    'optimal_pct': optimal/total*100,
    'hot_pct': hot/total*100,
    'cold_pct': cold/total*100,
    'optimal': optimal, 'hot': hot, 'cold': cold
}

# 照片数据
photos = [
    {'date': '2026-04-13', 'path': 'plant_images/day0413.jpg', 'desc': '最新状态 (4 月 13 日 09:25)'},
    {'date': '2026-04-11', 'path': 'plant_images/day0411.jpg', 'desc': '生长中期 (4 月 11 日 09:26)'},
    {'date': '2026-04-10', 'path': 'plant_images/day0410.jpg', 'desc': '生长早期 (4 月 10 日 09:25)'},
]

# 生成 HTML 报告
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>嘉宝果生长环境监测报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2E86AB, #A23B72); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 24px; margin-bottom: 10px; }}
        .content {{ padding: 25px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 18px; color: #2E86AB; margin-bottom: 15px; border-left: 4px solid #2E86AB; padding-left: 12px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 8px; padding: 15px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2E86AB; margin: 8px 0; }}
        .stat-label {{ color: #666; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #2E86AB; color: white; }}
        tr.optimal {{ background: rgba(106,153,78,0.1); }}
        tr.hot {{ background: rgba(199,62,29,0.1); }}
        tr.cold {{ background: rgba(52,152,219,0.1); }}
        .comfort-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }}
        .comfort-card {{ text-align: center; padding: 15px; border-radius: 8px; }}
        .comfort-card.optimal {{ background: rgba(106,153,78,0.15); border: 2px solid #6A994E; }}
        .comfort-card.hot {{ background: rgba(199,62,29,0.15); border: 2px solid #C73E1D; }}
        .comfort-card.cold {{ background: rgba(52,152,219,0.15); border: 2px solid #3498db; }}
        .comfort-pct {{ font-size: 24px; font-weight: bold; margin: 8px 0; }}
        .insights {{ background: linear-gradient(135deg, #fff3cd, #ffe69c); border-radius: 8px; padding: 15px; border-left: 4px solid #F18F01; }}
        .insight-item {{ margin: 12px 0; padding: 12px; background: white; border-radius: 6px; }}
        .insight-item h4 {{ color: #F18F01; margin-bottom: 6px; font-size: 14px; }}
        .insight-item p {{ color: #555; line-height: 1.5; font-size: 13px; }}
        .recommendations {{ background: linear-gradient(135deg, #d4edda, #c3e6cb); border-radius: 8px; padding: 15px; border-left: 4px solid #6A994E; }}
        .recommendations ul {{ margin-left: 20px; }}
        .recommendations li {{ margin: 8px 0; color: #155724; line-height: 1.5; font-size: 13px; }}
        .footer {{ text-align: center; padding: 15px; color: #999; font-size: 11px; border-top: 1px solid #eee; }}
        
        /* 照片画廊 */
        .photo-gallery {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
        .photo-card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .photo-card img {{ width: 100%; height: 200px; object-fit: cover; }}
        .photo-card .desc {{ padding: 12px; text-align: center; font-size: 13px; color: #555; background: #f8f9fa; }}
        .photo-card .date {{ font-weight: bold; color: #2E86AB; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌳 嘉宝果生长环境监测报告</h1>
            <p style="opacity:0.9;font-size:13px;">设备：PR20250416100005（植物生长记录仪）| 2026-04-01 ~ 2026-04-13</p>
        </div>
        <div class="content">
            <div class="section">
                <h2 class="section-title">📊 温度统计概览</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">平均温度</div>
                        <div class="stat-value">{stats['avg']:.1f}°C</div>
                        <div class="stat-label">{stats['count']} 个数据点</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">最高温度</div>
                        <div class="stat-value">{stats['max']:.1f}°C</div>
                        <div class="stat-label">适宜上限：{OPTIMAL_TEMP_MAX}°C</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">最低温度</div>
                        <div class="stat-value">{stats['min']:.1f}°C</div>
                        <div class="stat-label">适宜下限：{OPTIMAL_TEMP_MIN}°C</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">适宜范围</div>
                        <div class="stat-value">{OPTIMAL_TEMP_MIN}-{OPTIMAL_TEMP_MAX}°C</div>
                        <div class="stat-label">嘉宝果最适生长</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">🎯 温度适宜度分析</h2>
                <div class="comfort-grid">
                    <div class="comfort-card optimal">
                        <div>✅ 适宜</div>
                        <div class="comfort-pct" style="color:#6A994E">{comfort['optimal_pct']:.1f}%</div>
                        <div style="font-size:12px;color:#666">{comfort['optimal']} 个数据点</div>
                    </div>
                    <div class="comfort-card hot">
                        <div>🔥 偏热</div>
                        <div class="comfort-pct" style="color:#C73E1D">{comfort['hot_pct']:.1f}%</div>
                        <div style="font-size:12px;color:#666">{comfort['hot']} 个数据点</div>
                    </div>
                    <div class="comfort-card cold">
                        <div>❄️ 偏冷</div>
                        <div class="comfort-pct" style="color:#3498db">{comfort['cold_pct']:.1f}%</div>
                        <div style="font-size:12px;color:#666">{comfort['cold']} 个数据点</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📸 植物生长照片</h2>
                <div class="photo-gallery">
'''

for photo in photos:
    html += f'''
    <div class="photo-card">
        <img src="{photo['path']}" alt="{photo['date']}">
        <div class="desc">
            <div class="date">{photo['date']}</div>
            <div>{photo['desc']}</div>
        </div>
    </div>
'''

html += f'''
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📅 每日温度数据</h2>
                <table>
                    <thead>
                        <tr><th>日期</th><th>最低温</th><th>平均温</th><th>最高温</th><th>状态</th></tr>
                    </thead>
                    <tbody>
'''

for date, s in daily_stats.items():
    if s['avg'] < OPTIMAL_TEMP_MIN:
        status, cls = "❄️ 偏冷", "cold"
    elif s['avg'] > OPTIMAL_TEMP_MAX:
        status, cls = "🔥 偏热", "hot"
    else:
        status, cls = "✅ 适宜", "optimal"
    html += f'<tr class="{cls}"><td>{date}</td><td>{s["min"]:.1f}°C</td><td>{s["avg"]:.1f}°C</td><td>{s["max"]:.1f}°C</td><td>{status}</td></tr>\n'

# 洞察分析
temp_ranges = [s['max']-s['min'] for s in daily_stats.values()]
avg_range = sum(temp_ranges)/len(temp_ranges) if temp_ranges else 0

html += f'''
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2 class="section-title">💡 数据洞察与生长影响</h2>
                <div class="insights">
'''

if comfort['optimal_pct'] >= 60:
    html += f'''
    <div class="insight-item">
        <h4>✅ 整体环境优良</h4>
        <p>监测期间 {comfort['optimal_pct']:.1f}% 的时间温度处于嘉宝果适宜生长范围（{OPTIMAL_TEMP_MIN}-{OPTIMAL_TEMP_MAX}°C），有利于植株健康生长和果实发育。</p>
    </div>
'''
elif comfort['optimal_pct'] >= 40:
    html += f'''
    <div class="insight-item">
        <h4>⚠️ 环境基本适宜</h4>
        <p>监测期间 {comfort['optimal_pct']:.1f}% 的时间温度适宜，建议关注高温/低温时段的环境调控。</p>
    </div>
'''
else:
    html += f'''
    <div class="insight-item">
        <h4>🚨 高温胁迫预警</h4>
        <p>监测期间仅 {comfort['optimal_pct']:.1f}% 的时间温度适宜，{comfort['hot_pct']:.1f}% 的时间温度偏高。持续高温可能影响嘉宝果的正常生长和果实品质，建议采取遮阳降温措施。</p>
    </div>
'''

if comfort['hot_pct'] > 15:
    html += f'''
    <div class="insight-item">
        <h4>🔥 高温胁迫风险</h4>
        <p>监测期间 {comfort['hot_pct']:.1f}% 的时间温度超过 {OPTIMAL_TEMP_MAX}°C，最高达 {stats['max']:.1f}°C。持续高温可能导致：<br>
        • 叶片蒸腾作用过强，水分流失加速<br>
        • 光合作用效率下降<br>
        • 果实日灼风险增加<br>
        建议加强遮阳和喷雾降温措施。</p>
    </div>
'''

if avg_range > 10:
    html += f'''
    <div class="insight-item">
        <h4>📈 昼夜温差分析</h4>
        <p>平均昼夜温差 {avg_range:.1f}°C。较大温差有利于果实糖分积累，提升果实甜度，是嘉宝果品质形成的有利条件。</p>
    </div>
'''

html += f'''
    <div class="insight-item">
        <h4>🌱 当前生长阶段建议</h4>
        <p>4 月上旬为嘉宝果春梢生长期和花芽分化关键期。结合植物照片观察，建议：<br>
        • 保持土壤湿润（相对湿度 60-80%）<br>
        • 适时施用平衡型复合肥，促进花芽分化<br>
        • 注意防治炭疽病和蚜虫</p>
    </div>
</div></div>

<div class="section">
    <h2 class="section-title">📋 管理建议</h2>
    <div class="recommendations">
        <ul>
            <li><strong>遮阳措施：</strong>当日最高温超过 35°C 时，开启遮阳网（遮光率 50-60%），避免叶片灼伤</li>
            <li><strong>灌溉调整：</strong>高温时段（12:00-15:00）增加喷雾降温，保持土壤湿润但不积水</li>
            <li><strong>夜间保温：</strong>当夜间温度低于 18°C 时，考虑覆盖保温膜或熏烟防霜</li>
            <li><strong>通风管理：</strong>温度超过 32°C 时加强通风，促进空气流通，降低叶面温度</li>
            <li><strong>施肥建议：</strong>适宜温度期间可施用平衡型复合肥（N-P-K=15-15-15），促进花芽分化和果实发育</li>
            <li><strong>监测频率：</strong>保持当前 13 分钟/次的监测频率，设置温度异常告警（&lt;15°C 或 &gt;38°C）</li>
            <li><strong>病虫害防治：</strong>高温高湿环境易发炭疽病，定期喷施代森锰锌预防</li>
        </ul>
    </div>
</div>

<div class="footer">
    生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源：捷佳润 IoT 平台 | 分析模型：嘉宝果生长适宜度 v2.0
</div>
'''

html += '''
    </div>
</body>
</html>
'''

# 保存报告
output_path = '/home/cloud/.openclaw/workspace/reports/jaboticaba_report_v2.html'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ 报告 v2 已生成：{output_path}")
print(f"\n📊 数据摘要:")
print(f"   温度范围：{stats['min']:.1f}°C ~ {stats['max']:.1f}°C")
print(f"   平均温度：{stats['avg']:.1f}°C")
print(f"   适宜比例：{comfort['optimal_pct']:.1f}%")
print(f"   数据点数：{stats['count']}")
print(f"   植物照片：{len(photos)} 张")
