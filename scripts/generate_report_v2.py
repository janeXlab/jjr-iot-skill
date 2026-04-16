#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捷佳润 IoT 平台 - 生长环境数据可视化报告 v2（示例脚本，带植物照片）

用法:
    python3 generate_report_v2.py --config ../config.json --days 7 --output report.html
    python3 generate_report_v2.py --productKey YOUR_KEY --deviceName YOUR_NAME --days 7

注意：这是一个示例脚本，展示如何生成带照片的生长报告。
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
    parser = argparse.ArgumentParser(description='生长环境数据可视化报告 v2（示例，带照片）')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--productKey', type=str, help='产品 Key')
    parser.add_argument('--deviceName', type=str, help='设备名称')
    parser.add_argument('--days', type=int, default=7, help='分析天数（默认 7 天）')
    parser.add_argument('--output', type=str, default='report_v2.html', help='输出文件路径')
    parser.add_argument('--photos', type=str, help='照片目录路径（可选）')
    
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
    
    print(f"📊 开始生成报告 v2...")
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
        daily_stats[date] = {'max': max(vals), 'min': min(vals), 'avg': sum(vals)/len(vals)}
    
    # 适宜度分析
    total = len(temp_data)
    optimal = sum(1 for d in temp_data if 20 <= d['value'] <= 30)
    hot = sum(1 for d in temp_data if d['value'] > 30)
    cold = sum(1 for d in temp_data if d['value'] < 20)
    
    comfort = {
        'optimal_pct': optimal/total*100 if total else 0,
        'hot_pct': hot/total*100 if total else 0,
        'cold_pct': cold/total*100 if total else 0,
    }
    
    # 照片数据（示例，用户可自定义）
    photos_dir = args.photos or 'plant_images'
    photos = []
    if os.path.exists(photos_dir):
        for f in sorted(os.listdir(photos_dir))[:3]:  # 最多 3 张照片
            if f.endswith(('.jpg', '.png')):
                photos.append({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'path': os.path.join(photos_dir, f),
                    'desc': f'植物照片 ({f})'
                })
    
    # 生成 HTML 报告
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>生长环境监测报告 - {product_key}:{device_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #333; margin-bottom: 20px; border-left: 4px solid #667eea; padding-left: 15px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        .info-box {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #bbdefb; }}
        .info-row:last-child {{ border-bottom: none; }}
        .gallery {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }}
        .photo-card {{ background: #f8f9fa; border-radius: 8px; overflow: hidden; }}
        .photo-card img {{ width: 100%; height: 200px; object-fit: cover; }}
        .photo-info {{ padding: 15px; }}
        .photo-date {{ font-size: 14px; color: #666; }}
        .photo-desc {{ font-size: 13px; color: #999; margin-top: 5px; }}
        .chart-container {{ height: 400px; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 生长环境监测报告</h1>
            <p>设备：{product_key} : {device_name}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 监测概况</h2>
                <div class="info-box">
                    <div class="info-row">
                        <span>监测时段</span>
                        <span>{start_time.strftime('%Y-%m-%d')} ~ {end_time.strftime('%Y-%m-%d')}（{args.days}天）</span>
                    </div>
                    <div class="info-row">
                        <span>数据点数</span>
                        <span>{stats['count']}个</span>
                    </div>
                    <div class="info-row">
                        <span>生成时间</span>
                        <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🌡️ 温度统计</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{stats['avg']:.1f}°C</div>
                        <div class="stat-label">平均温度</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['max']:.1f}°C</div>
                        <div class="stat-label">最高温度</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['min']:.1f}°C</div>
                        <div class="stat-label">最低温度</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{stats['count']}</div>
                        <div class="stat-label">数据点数</div>
                    </div>
                </div>
                
                <div class="info-box">
                    <div class="info-row">
                        <span>🌡️ 适宜范围</span>
                        <span>20°C ~ 30°C</span>
                    </div>
                    <div class="info-row">
                        <span>✅ 适宜比例</span>
                        <span>{comfort['optimal_pct']:.1f}%</span>
                    </div>
                    <div class="info-row">
                        <span>🔥 偏高比例</span>
                        <span>{comfort['hot_pct']:.1f}%</span>
                    </div>
                    <div class="info-row">
                        <span>❄️ 偏低比例</span>
                        <span>{comfort['cold_pct']:.1f}%</span>
                    </div>
                </div>
            </div>
            
            {f'''
            <div class="section">
                <h2>📸 植物生长照片</h2>
                <div class="gallery">
                    {"".join(f"""
                    <div class="photo-card">
                        <img src="{photo['path']}" alt="{photo['desc']}" onerror="this.style.display='none'">
                        <div class="photo-info">
                            <div class="photo-date">{photo['date']}</div>
                            <div class="photo-desc">{photo['desc']}</div>
                        </div>
                    </div>
                    """ for photo in photos)}
                </div>
            </div>
            ''' if photos else ''}
        </div>
    </div>
</body>
</html>
'''
    
    # 保存
    output_path = args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成：{output_path}")
    print(f"📊 平均温度：{stats['avg']:.1f}°C")
    print(f"📈 适宜比例：{comfort['optimal_pct']:.1f}%")
    if photos:
        print(f"📸 包含照片：{len(photos)}张")

if __name__ == '__main__':
    main()
