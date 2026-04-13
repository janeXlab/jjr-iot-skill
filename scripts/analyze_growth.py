#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捷佳润 IoT 平台 - 嘉宝果生长环境数据分析
生成可视化图表和生长洞察报告
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from collections import defaultdict

# 颜色配置
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'success': '#6A994E',
    'bg': '#F8F9FA'
}

# 嘉宝果生长适宜条件（参考文献）
JABOTICABA_OPTIMAL = {
    'temp_min': 20,      # 最低适宜温度 °C
    'temp_max': 30,      # 最高适宜温度 °C
    'temp_optimal': 25,  # 最适温度 °C
    'humid_min': 60,     # 最低适宜湿度 %
    'humid_max': 80,     # 最高适宜湿度 %
    'humid_optimal': 70, # 最适湿度 %
}

def get_config():
    """从 config.json 读取配置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_token():
    """获取 API Token"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_script = os.path.join(script_dir, 'get_token.sh')
    result = subprocess.run([
        'bash', token_script
    ], capture_output=True, text=True)
    return result.stdout.strip().split('\n')[-1]

def fetch_property_data(identifier, start_time, end_time, token, product_key, device_name):
    """获取属性数据"""
    import urllib.request
    import urllib.parse
    
    base_url = "https://gateway.jjr.vip/iot/open/iot/device/propertyData"
    params = {
        'productKey': product_key,
        'deviceName': device_name,
        'identifier': identifier,
        'queryType': '2',
        'startTime': start_time,
        'endTime': end_time
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode())
    
    return data.get('result', [])

def parse_data(raw_data):
    """解析原始数据"""
    parsed = []
    for item in raw_data:
        try:
            parsed.append({
                'time': datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S'),
                'value': float(item['value'])
            })
        except (KeyError, ValueError):
            continue
    return parsed

def calculate_stats(data):
    """计算统计数据"""
    if not data:
        return {}
    
    values = [d['value'] for d in data]
    return {
        'count': len(values),
        'max': max(values),
        'min': min(values),
        'avg': sum(values) / len(values),
        'max_time': data[values.index(max(values))]['time'],
        'min_time': data[values.index(min(values))]['time'],
    }

def daily_stats(data):
    """按日统计"""
    daily = defaultdict(list)
    for d in data:
        date = d['time'].strftime('%Y-%m-%d')
        daily[date].append(d['value'])
    
    result = {}
    for date, values in sorted(daily.items()):
        result[date] = {
            'max': max(values),
            'min': min(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }
    return result

def comfort_analysis(data):
    """舒适度分析（基于嘉宝果适宜条件）"""
    total = len(data)
    optimal = sum(1 for d in data if JABOTICABA_OPTIMAL['temp_min'] <= d['value'] <= JABOTICABA_OPTIMAL['temp_max'])
    too_hot = sum(1 for d in data if d['value'] > JABOTICABA_OPTIMAL['temp_max'])
    too_cold = sum(1 for d in data if d['value'] < JABOTICABA_OPTIMAL['temp_min'])
    
    return {
        'optimal_percent': optimal / total * 100 if total > 0 else 0,
        'too_hot_percent': too_hot / total * 100 if total > 0 else 0,
        'too_cold_percent': too_cold / total * 100 if total > 0 else 0,
        'optimal_count': optimal,
        'too_hot_count': too_hot,
        'too_cold_count': too_cold,
    }

def generate_html_report(temp_data, humid_data, output_path):
    """生成 HTML 可视化报告"""
    
    # 计算统计数据
    temp_stats = calculate_stats(temp_data)
    humid_stats = calculate_stats(humid_data) if humid_data else {}
    temp_daily = daily_stats(temp_data)
    comfort = comfort_analysis(temp_data)
    
    # 生成每日数据表格 HTML
    daily_table_rows = ""
    for date, stats in temp_daily.items():
        # 判断温度是否适宜
        if stats['avg'] < JABOTICABA_OPTIMAL['temp_min']:
            status = "❄️ 偏冷"
            status_class = "cold"
        elif stats['avg'] > JABOTICABA_OPTIMAL['temp_max']:
            status = "🔥 偏热"
            status_class = "hot"
        else:
            status = "✅ 适宜"
            status_class = "optimal"
        
        daily_table_rows += f"""
        <tr class="{status_class}">
            <td>{date}</td>
            <td>{stats['min']:.1f}°C</td>
            <td>{stats['avg']:.1f}°C</td>
            <td>{stats['max']:.1f}°C</td>
            <td>{stats['count']}</td>
            <td>{status}</td>
        </tr>
        """
    
    # 生成洞察分析
    insights = generate_insights(temp_data, temp_stats, comfort)
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>嘉宝果生长环境监测报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: {COLORS['bg']}; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 20px; color: {COLORS['primary']}; margin-bottom: 15px; border-left: 4px solid {COLORS['primary']}; padding-left: 12px; }}
        
        /* 统计卡片 */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 10px; padding: 20px; text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: {COLORS['primary']}; margin: 10px 0; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        .stat-card.hot .stat-value {{ color: {COLORS['danger']}; }}
        .stat-card.cold .stat-value {{ color: #3498db; }}
        .stat-card.optimal .stat-value {{ color: {COLORS['success']}; }}
        
        /* 表格样式 */
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: {COLORS['primary']}; color: white; font-weight: 600; }}
        tr:hover {{ background: #f5f5f5; }}
        tr.optimal {{ background: rgba(106, 153, 78, 0.1); }}
        tr.hot {{ background: rgba(199, 62, 29, 0.1); }}
        tr.cold {{ background: rgba(52, 152, 219, 0.1); }}
        
        /* 洞察卡片 */
        .insights {{ background: linear-gradient(135deg, #fff3cd, #ffe69c); border-radius: 10px; padding: 20px; border-left: 4px solid {COLORS['warning']}; }}
        .insight-item {{ margin: 15px 0; padding: 15px; background: white; border-radius: 8px; }}
        .insight-item h4 {{ color: {COLORS['warning']}; margin-bottom: 8px; }}
        .insight-item p {{ color: #555; line-height: 1.6; }}
        
        /* 舒适度分析 */
        .comfort-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
        .comfort-card {{ text-align: center; padding: 20px; border-radius: 10px; }}
        .comfort-card.optimal {{ background: rgba(106, 153, 78, 0.15); border: 2px solid {COLORS['success']}; }}
        .comfort-card.hot {{ background: rgba(199, 62, 29, 0.15); border: 2px solid {COLORS['danger']}; }}
        .comfort-card.cold {{ background: rgba(52, 152, 219, 0.15); border: 2px solid #3498db; }}
        .comfort-percent {{ font-size: 28px; font-weight: bold; margin: 10px 0; }}
        
        /* 建议框 */
        .recommendations {{ background: linear-gradient(135deg, #d4edda, #c3e6cb); border-radius: 10px; padding: 20px; border-left: 4px solid {COLORS['success']}; }}
        .recommendations ul {{ margin-left: 20px; }}
        .recommendations li {{ margin: 10px 0; color: #155724; line-height: 1.6; }}
        
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌳 植物生长环境监测报告</h1>
            <p>设备：{device_name} | 报告周期：{start_date[:10]} ~ {end_date[:10]}</p>
        </div>
        
        <div class="content">
            <!-- 温度统计 -->
            <div class="section">
                <h2 class="section-title">📊 温度统计概览</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">平均温度</div>
                        <div class="stat-value">{temp_stats['avg']:.1f}°C</div>
                        <div class="stat-label">监测 {temp_stats['count']} 个数据点</div>
                    </div>
                    <div class="stat-card optimal">
                        <div class="stat-label">最高温度</div>
                        <div class="stat-value">{temp_stats['max']:.1f}°C</div>
                        <div class="stat-label">{temp_stats['max_time'].strftime('%m-%d %H:%M')}</div>
                    </div>
                    <div class="stat-card cold">
                        <div class="stat-label">最低温度</div>
                        <div class="stat-value">{temp_stats['min']:.1f}°C</div>
                        <div class="stat-label">{temp_stats['min_time'].strftime('%m-%d %H:%M')}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">适宜温度范围</div>
                        <div class="stat-value">{JABOTICABA_OPTIMAL['temp_min']}-{JABOTICABA_OPTIMAL['temp_max']}°C</div>
                        <div class="stat-label">嘉宝果最适生长</div>
                    </div>
                </div>
            </div>
            
            <!-- 舒适度分析 -->
            <div class="section">
                <h2 class="section-title">🎯 温度适宜度分析</h2>
                <div class="comfort-grid">
                    <div class="comfort-card optimal">
                        <div>✅ 适宜</div>
                        <div class="comfort-percent" style="color: {COLORS['success']}">{comfort['optimal_percent']:.1f}%</div>
                        <div>{comfort['optimal_count']} 个数据点</div>
                    </div>
                    <div class="comfort-card hot">
                        <div>🔥 偏热</div>
                        <div class="comfort-percent" style="color: {COLORS['danger']}">{comfort['too_hot_percent']:.1f}%</div>
                        <div>{comfort['too_hot_count']} 个数据点</div>
                    </div>
                    <div class="comfort-card cold">
                        <div>❄️ 偏冷</div>
                        <div class="comfort-percent" style="color: #3498db">{comfort['too_cold_percent']:.1f}%</div>
                        <div>{comfort['too_cold_count']} 个数据点</div>
                    </div>
                </div>
            </div>
            
            <!-- 每日数据表格 -->
            <div class="section">
                <h2 class="section-title">📅 每日温度数据</h2>
                <table>
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>最低温</th>
                            <th>平均温</th>
                            <th>最高温</th>
                            <th>数据点</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
                        {daily_table_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- 洞察分析 -->
            <div class="section">
                <h2 class="section-title">💡 数据洞察与生长影响</h2>
                <div class="insights">
                    {insights}
                </div>
            </div>
            
            <!-- 建议 -->
            <div class="section">
                <h2 class="section-title">📋 管理建议</h2>
                <div class="recommendations">
                    <ul>
                        <li><strong>遮阳措施：</strong>当日最高温超过 35°C 时，建议开启遮阳网，避免叶片灼伤</li>
                        <li><strong>灌溉调整：</strong>高温时段（12:00-15:00）增加喷雾降温，保持土壤湿润</li>
                        <li><strong>夜间保温：</strong>当夜间温度低于 18°C 时，考虑覆盖保温膜</li>
                        <li><strong>通风管理：</strong>温度超过 32°C 时加强通风，促进空气流通</li>
                        <li><strong>监测频率：</strong>建议保持当前 13 分钟/次的监测频率，及时发现异常</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源：捷佳润 IoT 平台 | 分析模型：嘉宝果生长适宜度 v1.0
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_content

def generate_insights(temp_data, temp_stats, comfort):
    """生成洞察分析"""
    insights = []
    
    # 温度适宜度洞察
    if comfort['optimal_percent'] >= 70:
        insights.append(f"""
        <h4>✅ 整体环境优良</h4>
        <p>监测期间 {comfort['optimal_percent']:.1f}% 的时间温度处于嘉宝果适宜生长范围（{JABOTICABA_OPTIMAL['temp_min']}-{JABOTICABA_OPTIMAL['temp_max']}°C），
        有利于植株健康生长和果实发育。</p>
        """)
    elif comfort['optimal_percent'] >= 50:
        insights.append(f"""
        <h4>⚠️ 环境基本适宜</h4>
        <p>监测期间 {comfort['optimal_percent']:.1f}% 的时间温度适宜，但仍有优化空间。建议关注高温/低温时段的环境调控。</p>
        """)
    else:
        insights.append(f"""
        <h4>🚨 环境需要改善</h4>
        <p>监测期间仅 {comfort['optimal_percent']:.1f}% 的时间温度适宜，超过 {100-comfort['optimal_percent']:.1f}% 的时间处于不适宜状态，
        可能影响嘉宝果的正常生长和果实品质。</p>
        """)
    
    # 高温洞察
    if comfort['too_hot_percent'] > 20:
        insights.append(f"""
        <h4>🔥 高温胁迫风险</h4>
        <p>监测期间 {comfort['too_hot_percent']:.1f}% 的时间温度超过 {JABOTICABA_OPTIMAL['temp_max']}°C，
        最高达 {temp_stats['max']:.1f}°C。持续高温可能导致：<br>
        • 叶片蒸腾作用过强，水分流失加速<br>
        • 光合作用效率下降<br>
        • 果实日灼风险增加<br>
        建议加强遮阳和喷雾降温措施。</p>
        """)
    
    # 温差洞察
    daily = daily_stats(temp_data)
    temp_ranges = [stats['max'] - stats['min'] for stats in daily.values()]
    avg_range = sum(temp_ranges) / len(temp_ranges) if temp_ranges else 0
    
    if avg_range > 12:
        insights.append(f"""
        <h4>📈 昼夜温差较大</h4>
        <p>平均昼夜温差 {avg_range:.1f}°C，较大温差有利于果实糖分积累，提升果实甜度。
        但需注意夜间低温可能导致的冷胁迫。</p>
        """)
    
    # 温度趋势洞察
    if daily:
        dates = list(daily.keys())
        first_week_avg = sum(daily[d]['avg'] for d in dates[:7]) / min(7, len(dates))
        second_week_avg = sum(daily[d]['avg'] for d in dates[7:14]) / min(7, len(dates[7:14])) if len(dates) > 7 else first_week_avg
        
        if second_week_avg > first_week_avg + 2:
            insights.append(f"""
            <h4>📈 温度呈上升趋势</h4>
            <p>第二周平均温度（{second_week_avg:.1f}°C）较第一周（{first_week_avg:.1f}°C）上升 {second_week_avg-first_week_avg:.1f}°C，
            符合春季气温回升规律。需提前做好高温应对准备。</p>
            """)
    
    return ''.join(insights)

def main():
    # 获取配置
    config = get_config()
    product_key = config.get('product_key', 'YOUR_PRODUCT_KEY')
    device_name = config.get('device_name', 'YOUR_DEVICE_NAME')

    # 计算日期范围 (最近 14 天)
    now = datetime.now()
    start_date = (now - timedelta(days=14)).strftime('%Y-%m-%d 00:00:00')
    end_date = now.strftime('%Y-%m-%d 23:59:59')

    # 获取数据
    print("🔍 获取 Token...")
    token = get_token()
    print(f"✅ Token 获取成功")
    
    print(f"📊 获取设备 {device_name} 的温度数据...")
    temp_raw = fetch_property_data('envTemp', start_date, end_date, token, product_key, device_name)
    temp_data = parse_data(temp_raw)
    print(f"✅ 获取 {len(temp_data)} 条温度数据")
    
    print("💧 获取湿度数据...")
    try:
        humid_raw = fetch_property_data('envHum', start_date, end_date, token, product_key, device_name)
        humid_data = parse_data(humid_raw)
        print(f"✅ 获取 {len(humid_data)} 条湿度数据")
    except Exception as e:
        print(f"⚠️ 湿度数据获取失败：{e}")
        humid_data = []
    
    # 生成报告
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), 'reports')
    output_path = os.path.join(output_dir, 'growth_report.html')
    os.makedirs(output_dir, exist_ok=True)
    
    print("📝 生成可视化报告...")
    generate_html_report(temp_data, humid_data, output_path)
    print(f"✅ 报告已生成：{output_path}")
    
    # 打印统计摘要
    print("\n" + "="*60)
    print("📊 数据摘要")
    print("="*60)
    if temp_data:
        values = [d['value'] for d in temp_data]
        print(f"温度范围：{min(values):.1f}°C ~ {max(values):.1f}°C")
        print(f"平均温度：{sum(values)/len(values):.1f}°C")
        print(f"数据点数：{len(values)}")

if __name__ == '__main__':
    main()
