#!/bin/bash
#
# 调用设备服务（如：拍照）
# 用法：./device_service_call.sh --productKey XXX --deviceName XXX --identifier XXX --input '{}'
#

set -e

# 默认配置
PRODUCT_KEY=""
DEVICE_NAME=""
IDENTIFIER=""
INPUT="{}"

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
        --identifier)
            IDENTIFIER="$2"
            shift 2
            ;;
        --input)
            INPUT="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 --productKey XXX --deviceName XXX --identifier XXX [--input '{}']"
            echo ""
            echo "选项:"
            echo "  --productKey    产品 Key（必填）"
            echo "  --deviceName    设备名称（必填）"
            echo "  --identifier    服务标识符（必填）- 如：takePhoto, camera 等"
            echo "  --input         输入参数（可选，JSON 格式）"
            exit 0
            ;;
        *)
            echo "未知参数：$1"
            exit 1
            ;;
    esac
done

# 加载配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在：$CONFIG_FILE"
    exit 1
fi

# 获取 Token
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
print(resp.json()['result']['accessToken'])
")

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 调用服务
echo "🔔 调用设备服务..."
echo "   产品 Key: $PRODUCT_KEY"
echo "   设备名称：$DEVICE_NAME"
echo "   服务标识：$IDENTIFIER"
echo "   输入参数：$INPUT"

# URL 编码 input 参数
INPUT_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$INPUT'))")

RESPONSE=$(curl -s --location --request POST \
  "https://gateway.jjr.vip/iot/open/iot/device/serveSet?productKey=$PRODUCT_KEY&deviceName=$DEVICE_NAME&identifier=$IDENTIFIER&input=$INPUT_ENCODED" \
  --header "Authorization: Bearer $TOKEN")

# 检查响应
CODE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', 0))")

if [ "$CODE" = "200" ]; then
    echo "✅ 服务调用成功！"
    echo "$RESPONSE" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2, ensure_ascii=False))"
else
    echo "❌ 服务调用失败：$RESPONSE"
    exit 1
fi
