#!/bin/bash
#
# 查询设备服务列表
# 用法：./list_device_services.sh --productKey XXX --deviceName XXX
#

set -e

# 默认配置
PRODUCT_KEY=""
DEVICE_NAME=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --productKey)
            PRODUCT_KEY="$2"
            shift 2
            ;;
        --deviceName)
            DEVICE_NAME="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 --productKey XXX --deviceName XXX"
            echo ""
            echo "选项:"
            echo "  --productKey    产品 Key（必填）"
            echo "  --deviceName    设备名称（必填）"
            exit 0
            ;;
        *)
            echo "未知参数：$1"
            exit 1
            ;;
    esac
done

# 检查必填参数
if [ -z "$PRODUCT_KEY" ] || [ -z "$DEVICE_NAME" ]; then
    echo "❌ 缺少必填参数"
    echo "用法：$0 --productKey XXX --deviceName XXX"
    exit 1
fi

# 加载配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在：$CONFIG_FILE"
    exit 1
fi

# 获取 Token
echo "🔑 获取 Token..."
TOKEN=$(python3 -c "
import json
import requests
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
resp = requests.post('https://gateway.jjr.vip/iot/oauth2/token', data={
    'grant_type': 'client_credentials',
    'client_id': config['client_id'],
    'client_secret': config['client_secret'],
    'scope': 'open'
})
result = resp.json()
if result.get('code') == 200:
    print(result['result']['accessToken'])
else:
    print('')
")

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 查询设备服务列表
echo "📋 查询设备服务列表..."
echo "   产品 Key: $PRODUCT_KEY"
echo "   设备名称：$DEVICE_NAME"
echo ""

# 重试最多 3 次
for i in 1 2 3; do
    RESPONSE=$(curl -s --location --request GET \
      "https://gateway.jjr.vip/iot/open/iot/device/serve?productKey=$PRODUCT_KEY&deviceName=$DEVICE_NAME" \
      --header "Authorization: Bearer $TOKEN")
    
    CODE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 0))")
    
    if [ "$CODE" = "200" ]; then
        break
    fi
    
    if [ $i -lt 3 ]; then
        echo "⚠️  第 $i 次尝试失败，等待 2 秒..."
        sleep 2
    fi
done

# 检查响应
if [ "$CODE" != "200" ]; then
    echo "❌ 查询失败：$RESPONSE"
    echo ""
    echo "💡 提示：服务器可能暂时不可用，请稍后重试"
    exit 1
fi

# 输出结果
echo "✅ 查询成功！"
echo ""

# 解析服务列表
SERVICES=$(echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
services = data.get('result', [])
if not services:
    print('[]')
else:
    print(json.dumps(services, ensure_ascii=False))
")

SERVICE_COUNT=$(echo "$SERVICES" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

if [ "$SERVICE_COUNT" = "0" ]; then
    echo "📭 该设备没有可用的服务"
    exit 0
fi

echo "📊 找到 $SERVICE_COUNT 个服务："
echo ""

# 格式化输出每个服务
echo "$SERVICES" | python3 -c "
import sys, json

services = json.load(sys.stdin)
for i, svc in enumerate(services, 1):
    identifier = svc.get('identifier', 'unknown')
    name = svc.get('name', '未知服务')
    print(f'{i}. 📌 {name} [{identifier}]')
    
    input_data = svc.get('inputData', [])
    if input_data:
        print('   输入参数:')
        for param in input_data:
            required = '必填' if param.get('required') else '可选'
            data_type = param.get('dataType', 'unknown')
            param_id = param.get('identifier', 'unknown')
            param_name = param.get('name', '未知')
            print(f'     • {param_id}: {param_name} ({data_type}, {required})')
            
            # 显示约束
            if param.get('enum'):
                print(f'       枚举值：{param.get(\"enum\")}')
            if param.get('min') is not None:
                print(f'       最小值：{param.get(\"min\")}')
            if param.get('max') is not None:
                print(f'       最大值：{param.get(\"max\")}')
    else:
        print('   输入参数：无')
    
    output_data = svc.get('outputData', [])
    if output_data:
        print('   输出参数:')
        for param in output_data:
            data_type = param.get('dataType', 'unknown')
            param_id = param.get('identifier', 'unknown')
            param_name = param.get('name', '未知')
            print(f'     • {param_id}: {param_name} ({data_type})')
    else:
        print('   输出参数：无')
    
    print()
"

echo "💡 提示：使用以下命令调用服务"
echo "   ./device_service_call.sh \\"
echo "     --productKey $PRODUCT_KEY \\"
echo "     --deviceName $DEVICE_NAME \\"
echo "     --identifier <服务标识> \\"
echo "     --input '{\"参数名\":\"参数值\"}'"
