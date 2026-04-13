#!/bin/bash
#
# 捷佳润 IoT 平台 - 查询设备属性列表脚本
# 用法：./list_properties.sh --productKey xxx --deviceName xxx
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"
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
            echo "用法：$0 --productKey PRODUCT_KEY --deviceName DEVICE_NAME"
            echo ""
            echo "必需参数:"
            echo "  --productKey  产品 Key"
            echo "  --deviceName  设备名称"
            echo "  --help        显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [ -z "$PRODUCT_KEY" ] || [ -z "$DEVICE_NAME" ]; then
    echo "❌ 缺少必需参数"
    echo "请使用 --help 查看用法"
    exit 1
fi

# 获取 Token
TOKEN=$(/bin/bash "$(dirname "$0")/get_token.sh" --config "$CONFIG_FILE" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 查询属性列表
echo "🔍 查询设备属性列表..."
echo "   产品 Key: $PRODUCT_KEY"
echo "   设备名称：$DEVICE_NAME"
echo ""

RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/device/property?productKey=${PRODUCT_KEY}&deviceName=${DEVICE_NAME}" \
    --header "Authorization: Bearer ${TOKEN}")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
if [ "$CODE" != "200" ]; then
    echo "❌ 查询失败：$RESPONSE"
    exit 1
fi

# 检查是否有数据
RECORD_COUNT=$(echo "$RESPONSE" | jq -r '.result.records | length')
if [ "$RECORD_COUNT" = "0" ] || [ "$RECORD_COUNT" = "null" ]; then
    echo "⚠️  未找到属性信息"
    exit 0
fi

# 显示属性列表
echo "✅ 查询成功"
echo ""
echo "📋 设备属性列表:"
echo ""
echo "$RESPONSE" | jq -r '
.result.records[] |
"| \(.identifier) | \(.name) | \(.type) | \(.unit // "-") | \(.description // "无描述") |"
' | column -t -s '|'

echo ""
echo "📊 属性总数：$RECORD_COUNT"
echo ""
echo "💡 提示：查询属性数据时，使用 identifier 作为参数"
echo "   例如：./get_property_data.sh --productKey $PRODUCT_KEY --deviceName $DEVICE_NAME --identifier envTemp"
