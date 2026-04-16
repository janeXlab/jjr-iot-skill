#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捷佳润 IoT 平台 - 生长环境数据分析
生成可视化图表和生长洞察报告

用法:
    python3 analyze_growth.py --config ../config.json --days 7
    python3 analyze_growth.py --productKey YOUR_KEY --deviceName YOUR_NAME --days 7
"""

import json
import subprocess
import os
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# 颜色配置
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'success': '#6A994E',
    'bg': '#F8F9FA'
}

# 植物生长适宜条件（通用配置，可在 config.json 中覆盖）
DEFAULT_OPTIMAL = {
    'temp_min': 20,      # 最低适宜温度 °C
    'temp_max': 30,      # 最高适宜温度 °C
    'temp_optimal': 25,  # 最适温度 °C
    'humid_min': 60,     # 最低适宜湿度 %
    'humid_max': 80,     # 最高适宜湿度 %
    'humid_optimal': 70, # 最适湿度 %
}

def load_config(config_path=None):
    """加载配置文件"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
    # 尝试默认路径
    default_paths = [
        'config.json',
        os.path.join(os.path.dirname(__file__), 'config.json'),
        os.path.expanduser('~/.jjr-iot/config.json')
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    
    return None

def get_token(config):
    """获取 API Token"""
    script_path = os.path.join(os.path.dirname(__file__), 'get_token.sh')
    result = subprocess.run(['bash', script_path], capture_output=True, text=True)
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
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
        return data.get('result', [])
    except Exception as e:
        print(f"⚠️  获取数据失败：{e}")
        return []

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
            'avg': sum(values) / len(values),
            'max': max(values),
            'min': min(values),
            'count': len(values)
        }
    return result

def generate_html_report(temp_data, humid_data, optimal, device_info, days):
    """生成 HTML 报告"""
    from datetime import datetime
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>生长环境分析报告 - {device_info['productKey']}:{device_info['deviceName']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #F8F9FA; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2E86AB; text-align: center; }}
        .info {{ background: #E3F2FD; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #F8F9FA; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #2E86AB; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2E86AB; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .chart-container {{ position: relative; height: 400px; margin: 30px 0; }}
        .optimal {{ background: #E8F5E9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .warning {{ color: #F18F01; }}
        .danger {{ color: #C73E1D; }}
        .success {{ color: #6A994E; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 生长环境分析报告</h1>
        
        <div class="info">
            <strong>设备信息：</strong> {device_info['productKey']} : {device_info['deviceName']}<br>
            <strong>分析时段：</strong> 近 {days} 天<br>
            <strong>生成时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <h2>📊 温度统计</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{temp_data['stats']['avg']:.1f}°C</div>
                <div class="stat-label">平均温度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{temp_data['stats']['max']:.1f}°C</div>
                <div class="stat-label">最高温度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{temp_data['stats']['min']:.1f}°C</div>
                <div class="stat-label">最低温度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{temp_data['stats']['count']}</div>
                <div class="stat-label">数据点数</div>
            </div>
        </div>
        
        <div class="optimal">
            <strong>🌡️ 适宜温度范围：</strong> {optimal['temp_min']}°C ~ {optimal['temp_max']}°C<br>
            <strong>📈 适宜比例：</strong> 
            <span class="{temp_data['optimal_ratio_class']}">{temp_data['optimal_ratio']:.1f}%</span>
        </div>
        
        <div class="chart-container">
            <canvas id="tempChart"></canvas>
        </div>
        
        <h2>💧 湿度统计</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{humid_data['stats']['avg']:.1f}%</div>
                <div class="stat-label">平均湿度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{humid_data['stats']['max']:.1f}%</div>
                <div class="stat-label">最高湿度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{humid_data['stats']['min']:.1f}%</div>
                <div class="stat-label">最低湿度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{humid_data['stats']['count']}</div>
                <div class="stat-label">数据点数</div>
            </div>
        </div>
        
        <div class="optimal">
            <strong>💧 适宜湿度范围：</strong> {optimal['humid_min']}% ~ {optimal['humid_max']}%<br>
            <strong>📈 适宜比例：</strong> 
            <span class="{humid_data['optimal_ratio_class']}">{humid_data['optimal_ratio']:.1f}%</span>
        </div>
        
        <div class="chart-container">
            <canvas id="humidChart"></canvas>
        </div>
        
        <h2>💡 生长建议</h2>
        <div class="info">
            {generate_recommendations(temp_data, humid_data, optimal)}
        </div>
    </div>
    
    <script>
        // 温度图表
        new Chart(document.getElementById('tempChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(temp_data['daily_labels'])},
                datasets: [{{
                    label: '温度 (°C)',
                    data: {json.dumps(temp_data['daily_avg'])},
                    borderColor: '{COLORS['primary']}',
                    backgroundColor: '{COLORS['primary']}20',
                    tension: 0.4,
                    fill: true
                }}, {{
                    label: '适宜范围',
                    data: [{optimal['temp_min']}] * {len(temp_data['daily_avg'])},
                    borderColor: '{COLORS['success']}',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }}, {{
                    label: '适宜范围',
                    data: [{optimal['temp_max']}] * {len(temp_data['daily_avg'])},
                    borderColor: '{COLORS['success']}',
                    borderDash: [5, 5],
                    fill: '+1',
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{ display: true, text: '温度变化趋势' }}
                }}
            }}
        }});
        
        // 湿度图表
        new Chart(document.getElementById('humidChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(humid_data['daily_labels'])},
                datasets: [{{
                    label: '湿度 (%)',
                    data: {json.dumps(humid_data['daily_avg'])},
                    borderColor: '{COLORS['secondary']}',
                    backgroundColor: '{COLORS['secondary']}20',
                    tension: 0.4,
                    fill: true
                }}, {{
                    label: '适宜范围',
                    data: [{optimal['humid_min']}] * {len(humid_data['daily_avg'])},
                    borderColor: '{COLORS['success']}',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }}, {{
                    label: '适宜范围',
                    data: [{optimal['humid_max']}] * {len(humid_data['daily_avg'])},
                    borderColor: '{COLORS['success']}',
                    borderDash: [5, 5],
                    fill: '+1',
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{ display: true, text: '湿度变化趋势' }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html

def generate_recommendations(temp_data, humid_data, optimal):
    """生成建议"""
    recommendations = []
    
    # 温度建议
    temp_avg = temp_data['stats']['avg']
    if temp_avg < optimal['temp_min']:
        recommendations.append(f"⚠️ <strong>温度偏低</strong>：平均温度 {temp_avg:.1f}°C 低于适宜范围，建议采取保温措施。")
    elif temp_avg > optimal['temp_max']:
        recommendations.append(f"⚠️ <strong>温度偏高</strong>：平均温度 {temp_avg:.1f}°C 高于适宜范围，建议加强通风或遮阳。")
    else:
        recommendations.append(f"✅ <strong>温度适宜</strong>：平均温度 {temp_avg:.1f}°C 在适宜范围内。")
    
    # 湿度建议
    humid_avg = humid_data['stats']['avg']
    if humid_avg < optimal['humid_min']:
        recommendations.append(f"⚠️ <strong>湿度偏低</strong>：平均湿度 {humid_avg:.1f}% 低于适宜范围，建议增加灌溉。")
    elif humid_avg > optimal['humid_max']:
        recommendations.append(f"⚠️ <strong>湿度偏高</strong>：平均湿度 {humid_avg:.1f}% 高于适宜范围，注意预防病害。")
    else:
        recommendations.append(f"✅ <strong>湿度适宜</strong>：平均湿度 {humid_avg:.1f}% 在适宜范围内。")
    
    return "<ul>" + "".join(f"<li style='margin: 10px 0;'>{r}</li>" for r in recommendations) + "</ul>"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='捷佳润 IoT 平台 - 生长环境数据分析')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--productKey', type=str, help='产品 Key')
    parser.add_argument('--deviceName', type=str, help='设备名称')
    parser.add_argument('--days', type=int, default=7, help='分析天数（默认 7 天）')
    parser.add_argument('--output', type=str, default='growth_report.html', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    if not config:
        print("❌ 错误：未找到配置文件，请先运行 setup_credentials.sh 配置")
        sys.exit(1)
    
    # 获取设备信息（参数优先，其次配置文件）
    product_key = args.productKey or config.get('product_key')
    device_name = args.deviceName or config.get('device_name')
    
    if not product_key or not device_name:
        print("❌ 错误：请提供产品 Key 和设备名称")
        print("用法:")
        print("  python3 analyze_growth.py --productKey YOUR_KEY --deviceName YOUR_NAME")
        print("  或在 config.json 中配置 product_key 和 device_name")
        sys.exit(1)
    
    # 获取植物类型配置（可选）
    plant_type = config.get('plant_type', 'default')
    optimal = config.get('optimal_conditions', DEFAULT_OPTIMAL)
    
    print(f"🌱 开始分析生长环境数据...")
    print(f"   设备：{product_key}:{device_name}")
    print(f"   时段：近 {args.days} 天")
    print(f"   植物类型：{plant_type}")
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=args.days)
    
    # 获取 Token
    token = get_token(config)
    if not token:
        print("❌ 错误：无法获取 Token，请检查配置")
        sys.exit(1)
    
    # 获取温度数据
    print("📊 获取温度数据...")
    temp_raw = fetch_property_data('envTemp', start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                                    end_time.strftime('%Y-%m-%d %H:%M:%S'), token, 
                                    product_key, device_name)
    temp_data = parse_data(temp_raw)
    print(f"   获取到 {len(temp_data)} 个数据点")
    
    # 获取湿度数据
    print("💧 获取湿度数据...")
    humid_raw = fetch_property_data('envHum', start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                                     end_time.strftime('%Y-%m-%d %H:%M:%S'), token, 
                                     product_key, device_name)
    humid_data = parse_data(humid_raw)
    print(f"   获取到 {len(humid_data)} 个数据点")
    
    if not temp_data and not humid_data:
        print("⚠️  警告：未获取到任何数据，请检查设备是否在线")
        sys.exit(1)
    
    # 计算统计数据
    temp_stats = calculate_stats(temp_data)
    humid_stats = calculate_stats(humid_data)
    
    # 计算适宜比例
    temp_optimal_count = sum(1 for d in temp_data if optimal['temp_min'] <= d['value'] <= optimal['temp_max'])
    humid_optimal_count = sum(1 for d in humid_data if optimal['humid_min'] <= d['value'] <= optimal['humid_max'])
    
    temp_optimal_ratio = (temp_optimal_count / len(temp_data) * 100) if temp_data else 0
    humid_optimal_ratio = (humid_optimal_count / len(humid_data) * 100) if humid_data else 0
    
    # 准备图表数据
    temp_daily = daily_stats(temp_data)
    humid_daily = daily_stats(humid_data)
    
    # 生成报告数据结构
    temp_report = {
        'stats': temp_stats,
        'daily_labels': list(temp_daily.keys()),
        'daily_avg': [temp_daily[d]['avg'] for d in temp_daily.keys()],
        'optimal_ratio': temp_optimal_ratio,
        'optimal_ratio_class': 'success' if temp_optimal_ratio > 80 else 'warning' if temp_optimal_ratio > 50 else 'danger'
    }
    
    humid_report = {
        'stats': humid_stats,
        'daily_labels': list(humid_daily.keys()),
        'daily_avg': [humid_daily[d]['avg'] for d in humid_daily.keys()],
        'optimal_ratio': humid_optimal_ratio,
        'optimal_ratio_class': 'success' if humid_optimal_ratio > 80 else 'warning' if humid_optimal_ratio > 50 else 'danger'
    }
    
    device_info = {
        'productKey': product_key,
        'deviceName': device_name
    }
    
    # 生成 HTML 报告
    print("📝 生成分析报告...")
    html = generate_html_report(temp_report, humid_report, optimal, device_info, args.days)
    
    # 保存报告
    output_path = args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成：{output_path}")
    print(f"📊 温度：平均 {temp_stats.get('avg', 0):.1f}°C, 适宜率 {temp_optimal_ratio:.1f}%")
    print(f"💧 湿度：平均 {humid_stats.get('avg', 0):.1f}%, 适宜率 {humid_optimal_ratio:.1f}%")

if __name__ == '__main__':
    main()
