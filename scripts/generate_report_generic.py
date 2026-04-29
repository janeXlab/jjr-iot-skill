#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捷佳润 IoT 平台 - 通用环境监测报告生成器

支持任意作物/场景的环境监测数据可视化，参数通过配置文件或命令行指定。

用法:
    python3 generate_report_generic.py \
      --config config.json \
      --output /path/to/output.png \
      --title "环境监测报告"
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在：{config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_report(data, config, output_path):
    """生成报告"""
    from playwright.sync_api import sync_playwright
    
    # 从配置中读取参数
    title = config.get("title", "环境监测报告")
    device_name = config.get("deviceName", "未知设备")
    crop_type = config.get("cropType", "作物")  # 作物类型（如：鹿茸菇、番茄等）
    
    # 从配置中读取标准参数（不同作物有不同的标准）
    standards = config.get("standards", {
        "temp": {"min": 15, "max": 25, "unit": "°C"},
        "humidity": {"min": 60, "max": 80, "unit": "%"},
        "co2": {"min": 0, "max": 1000, "unit": "ppm"},
        "light": {"min": 0, "max": 1000, "unit": "lux"}
    })
    
    # 生成 HTML
    html = generate_html(data, config, standards, title, device_name, crop_type)
    
    # 写入 HTML 文件
    html_path = output_path.replace('.png', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML 报告已生成：{html_path}")
    
    # 使用 Playwright 生成 PNG
    print(f"📸 正在生成 PNG 截图...")
    
    # 启动本地 HTTP 服务器
    import subprocess
    import time
    server = subprocess.Popen(
        ['python3', '-m', 'http.server', '8888', '--directory', os.path.dirname(html_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)
    
    try:
        with sync_playwright() as p:
            # Chromium 路径可通过环境变量 CHROMIUM_PATH 配置
            chromium_path = os.environ.get('CHROMIUM_PATH', '/snap/bin/chromium')
            browser = p.chromium.launch(
                executable_path=chromium_path,
                headless=True,
                args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
            )
            page = browser.new_page()
            page.set_viewport_size({"width": 1400, "height": 900})
            page.goto(f"http://localhost:8888/{os.path.basename(html_path)}", wait_until="networkidle")
            page.screenshot(path=output_path, full_page=True)
            browser.close()
    finally:
        server.terminate()
        server.wait()
    
    print(f"✅ PNG 截图已生成：{output_path}")

def generate_html(data, config, standards, title, device_name, crop_type):
    """生成 HTML 报告"""
    import json as json_module
    
    timestamps = [d["time"] for d in data["temperature"]]
    temps = [d["value"] for d in data["temperature"]]
    humidities = [d["value"] for d in data["humidity"]]
    co2s = [d["value"] for d in data["co2"]]
    lights = [d["value"] for d in data["light"]]
    
    # 计算统计数据
    def calc_stats(values):
        return {"min": min(values), "max": max(values), "avg": sum(values) / len(values)}
    
    temp_stats = calc_stats(temps)
    humidity_stats = calc_stats(humidities)
    co2_stats = calc_stats(co2s)
    light_stats = calc_stats(lights)
    
    start_time = timestamps[0].split(" ")[1][:5]
    end_time = timestamps[-1].split(" ")[1][:5]
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Microsoft YaHei", Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header p {{ opacity: 0.9; font-size: 13px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .stat-card h3 {{ font-size: 13px; color: #666; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 20px; font-weight: bold; color: #333; }}
        .stat-card .std {{ font-size: 11px; color: #999; margin-top: 4px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 20px; }}
        .chart-container h2 {{ color: #333; margin-bottom: 15px; font-size: 16px; }}
        .chart-wrapper {{ position: relative; height: 400px; }}
        .footer {{ text-align: center; color: #999; margin-top: 15px; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 {title}</h1>
            <p>设备：{device_name} | 作物类型：{crop_type} | 时段：{start_time} 至 {end_time}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>🌡️ 温度</h3>
                <div class="value">{temp_stats["avg"]:.1f}°C</div>
                <div class="std">范围：{temp_stats["min"]:.1f}~{temp_stats["max"]:.1f}°C</div>
                <div class="std">标准：{standards["temp"]["min"]}-{standards["temp"]["max"]}°C</div>
            </div>
            <div class="stat-card">
                <h3>💧 湿度</h3>
                <div class="value">{humidity_stats["avg"]:.1f}%</div>
                <div class="std">范围：{humidity_stats["min"]:.1f}~{humidity_stats["max"]:.1f}%</div>
                <div class="std">标准：{standards["humidity"]["min"]}-{standards["humidity"]["max"]}%</div>
            </div>
            <div class="stat-card">
                <h3>🌫️ CO₂</h3>
                <div class="value">{co2_stats["avg"]:.0f} ppm</div>
                <div class="std">范围：{co2_stats["min"]:.0f}~{co2_stats["max"]:.0f} ppm</div>
                <div class="std">标准：≤{standards["co2"]["max"]} ppm</div>
            </div>
            <div class="stat-card">
                <h3>☀️ 光照</h3>
                <div class="value">{light_stats["avg"]:.0f} lux</div>
                <div class="std">范围：{light_stats["min"]:.0f}~{light_stats["max"]:.0f} lux</div>
                <div class="std">标准：{standards["light"]["min"]}-{standards["light"]["max"]} lux</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📈 环境参数趋势图</h2>
            <div class="chart-wrapper">
                <canvas id="mainChart"></canvas>
            </div>
        </div>
        
        <div class="footer">
            <p>生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 数据来源：捷佳润物联平台</p>
        </div>
    </div>
    
    <script>
        const labels = {json_module.dumps([t.split(" ")[1][:5] for t in timestamps])};
        const tempData = {json_module.dumps(temps)};
        const humidityData = {json_module.dumps(humidities)};
        const co2Data = {json_module.dumps(co2s)};
        const lightData = {json_module.dumps(lights)};
        
        new Chart(document.getElementById('mainChart'), {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: '温度 (°C)',
                        data: tempData,
                        borderColor: '#ff6384',
                        yAxisID: 'y',
                        tension: 0.3
                    }},
                    {{
                        label: '湿度 (%)',
                        data: humidityData,
                        borderColor: '#36a2eb',
                        yAxisID: 'y1',
                        tension: 0.3,
                        borderDash: [5, 5]
                    }},
                    {{
                        label: 'CO₂ (ppm)',
                        data: co2Data,
                        borderColor: '#ffce56',
                        yAxisID: 'y2',
                        tension: 0.3
                    }},
                    {{
                        label: '光照 (lux)',
                        data: lightData,
                        borderColor: '#4bc0c0',
                        yAxisID: 'y3',
                        tension: 0.3,
                        borderDash: [5, 5]
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ display: true, title: {{ display: true, text: '时间' }} }},
                    y: {{ type: 'linear', display: true, position: 'left', title: {{ display: true, text: '温度 (°C)' }}, min: {standards["temp"]["min"]-5}, max: {standards["temp"]["max"]+5} }},
                    y1: {{ type: 'linear', display: true, position: 'left', title: {{ display: true, text: '湿度 (%)' }}, min: {standards["humidity"]["min"]-20}, max: 100, grid: {{ drawOnChartArea: false }} }},
                    y2: {{ type: 'linear', display: true, position: 'right', title: {{ display: true, text: 'CO₂ (ppm)' }}, min: 0, max: {standards["co2"]["max"]*2}, grid: {{ drawOnChartArea: false }} }},
                    y3: {{ type: 'linear', display: false, min: 0, max: 1000 }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    parser = argparse.ArgumentParser(description='通用环境监测报告生成器')
    parser.add_argument('--config', required=True, help='配置文件路径（JSON）')
    parser.add_argument('--output', required=True, help='输出 PNG 文件路径')
    parser.add_argument('--data', help='数据文件路径（JSON，可选，否则从 API 获取）')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 加载数据
    if args.data and os.path.exists(args.data):
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("❌ 请提供数据文件 --data")
        sys.exit(1)
    
    # 生成报告
    generate_report(data, config, args.output)

if __name__ == "__main__":
    main()
