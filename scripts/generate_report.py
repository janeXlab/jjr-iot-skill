#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捷佳润 IoT 平台 - 生长环境数据可视化报告（示例脚本）

用法:
    python3 generate_report.py --config ../config.json --days 7 --output report.html

注意：这是一个示例脚本，展示如何使用 API 生成可视化报告。
      生产环境请使用 analyze_growth.py（支持更多功能和配置）。
"""

import json
import subprocess
import os
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

def load_config(config_path=None):
    """加载配置文件"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
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

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生长环境数据可视化报告（示例）')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--productKey', type=str, help='产品 Key')
    parser.add_argument('--deviceName', type=str, help='设备名称')
    parser.add_argument('--days', type=int, default=7, help='分析天数（默认 7 天）')
    parser.add_argument('--output', type=str, default='report.html', help='输出文件路径')
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    if not config:
        print("❌ 错误：未找到配置文件")
        sys.exit(1)
    
    product_key = args.productKey or config.get('product_key')
    device_name = args.deviceName or config.get('device_name')
    
    if not product_key or not device_name:
        print("❌ 错误：请提供产品 Key 和设备名称")
        sys.exit(1)
    
    print(f"📊 开始生成报告...")
    print(f"   设备：{product_key}:{device_name}")
    print(f"   时段：近 {args.days} 天")
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=args.days)
    
    token = get_token(config)
    if not token:
        print("❌ 错误：无法获取 Token")
        sys.exit(1)
    
    print("📊 获取温度数据...")
    temp_raw = fetch_property_data('envTemp', start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                                    end_time.strftime('%Y-%m-%d %H:%M:%S'), token, 
                                    product_key, device_name)
    print(f"   获取到 {len(temp_raw)} 个数据点")
    
    if not temp_raw:
        print("⚠️  警告：未获取到数据")
        sys.exit(1)
    
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
        daily_stats[date] = {
            'avg': sum(vals) / len(vals),
            'max': max(vals),
            'min': min(vals)
        }
    
    # 计算适宜比例
    optimal_count = sum(1 for v in values if 20 <= v <= 30)
    optimal_ratio = optimal_count / len(values) * 100 if values else 0
    
    # 生成 HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>生长环境报告 - {product_key}:{device_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #F8F9FA; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2E86AB; }}
        .info {{ background: #E3F2FD; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #F8F9FA; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-value {{ font-size: 20px; font-weight: bold; color: #2E86AB; }}
        .chart-container {{ height: 400px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 生长环境报告</h1>
        
        <div class="info">
            <strong>设备：</strong> {product_key} : {device_name}<br>
            <strong>时段：</strong> {start_time.strftime('%Y-%m-%d')} ~ {end_time.strftime('%Y-%m-%d')}<br>
            <strong>生成时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <h2>📊 温度统计</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{stats['avg']:.1f}°C</div>
                <div>平均温度</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['max']:.1f}°C</div>
                <div>最高温度</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['min']:.1f}°C</div>
                <div>最低温度</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['count']}</div>
                <div>数据点数</div>
            </div>
        </div>
        
        <div class="info">
            <strong>🌡️ 适宜范围：</strong> 20°C ~ 30°C<br>
            <strong>📈 适宜比例：</strong> {optimal_ratio:.1f}%
        </div>
        
        <div class="chart-container">
            <canvas id="tempChart"></canvas>
        </div>
    </div>
    
    <script>
        new Chart(document.getElementById('tempChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(list(daily_stats.keys()))},
                datasets: [{{
                    label: '平均温度 (°C)',
                    data: {json.dumps([daily_stats[d]['avg'] for d in daily_stats.keys()])},
                    borderColor: '#2E86AB',
                    backgroundColor: '#2E86AB20',
                    tension: 0.4,
                    fill: true
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
    </script>
</body>
</html>
"""
    
    # 保存
    output_path = args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成：{output_path}")
    print(f"📊 平均温度：{stats['avg']:.1f}°C")
    print(f"📈 适宜比例：{optimal_ratio:.1f}%")

if __name__ == '__main__':
    main()
