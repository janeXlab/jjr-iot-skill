#!/bin/bash
#
# 捷佳润 IoT 平台 - 查询属性数据脚本
# 用法：./get_property_data.sh --productKey xxx --deviceName xxx --identifier xxx --startTime "xxx" --endTime "xxx"
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"

# 必需参数
PRODUCT_KEY=""
DEVICE_NAME=""
IDENTIFIER=""
START_TIME=""
END_TIME=""
QUERY_TYPE="2"
LIMIT=""

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
        --startTime)
            START_TIME="$2"
            shift 2
            ;;
        --endTime)
            END_TIME="$2"
            shift 2
            ;;
        --queryType)
            QUERY_TYPE="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 --productKey XXX --deviceName XXX --identifier XXX --startTime \"XXX\" --endTime \"XXX\""
            echo ""
            echo "必需参数:"
            echo "  --productKey   产品 Key"
            echo "  --deviceName   设备名称"
            echo "  --identifier   属性标识 (如：envTemp, envHum, imgUrl)"
            echo "  --startTime    开始时间 (格式：YYYY-MM-DD HH:MM:SS)"
            echo "  --endTime      结束时间 (格式：YYYY-MM-DD HH:MM:SS)"
            echo ""
            echo "可选参数:"
            echo "  --queryType    查询类型 (默认：2)"
            echo "  --limit        返回条数限制"
            echo "  --config       配置文件路径"
            echo "  --help         显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [ -z "$PRODUCT_KEY" ] || [ -z "$DEVICE_NAME" ] || [ -z "$IDENTIFIER" ] || [ -z "$START_TIME" ] || [ -z "$END_TIME" ]; then
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

# URL 编码时间参数
START_TIME_ENCODED=$(echo "$START_TIME" | sed 's/ /%20/g')
END_TIME_ENCODED=$(echo "$END_TIME" | sed 's/ /%20/g')

# 构建查询参数
QUERY_PARAMS="productKey=${PRODUCT_KEY}&deviceName=${DEVICE_NAME}&identifier=${IDENTIFIER}&queryType=${QUERY_TYPE}&startTime=${START_TIME_ENCODED}&endTime=${END_TIME_ENCODED}"

# 查询属性数据
RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/device/propertyData?${QUERY_PARAMS}" \
    --header "Authorization: Bearer ${TOKEN}")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
if [ "$CODE" != "200" ]; then
    echo "❌ 查询失败：$RESPONSE"
    exit 1
fi

# 输出结果
echo "✅ 查询成功"
echo ""
echo "📋 查询条件:"
echo "   产品 Key: $PRODUCT_KEY"
echo "   设备名称：$DEVICE_NAME"
echo "   属性标识：$IDENTIFIER"
echo "   时间范围：$START_TIME ~ $END_TIME"
echo ""

# 检查是否有数据
RECORD_COUNT=$(echo "$RESPONSE" | jq -r '.result | length')
if [ "$RECORD_COUNT" = "0" ] || [ "$RECORD_COUNT" = "null" ]; then
    echo "⚠️  未找到数据"
    exit 0
fi

echo "📊 数据条数：$RECORD_COUNT"
echo ""

# 输出数据（限制条数）
if [ -n "$LIMIT" ]; then
    echo "$RESPONSE" | jq -r ".result[:$LIMIT] | .[] | \"| \(.time) | \(.value) |\"" | column -t -s '|'
else
    echo "$RESPONSE" | jq -r '.result[] | "| \(.time) | \(.value) |"' | column -t -s '|'
fi

# 输出统计信息
if [ "$IDENTIFIER" = "envTemp" ]; then
    echo ""
    echo "🌡️  温度统计:"
    echo "$RESPONSE" | jq -r '
        .result | 
        map(.value | tonumber) |
        "   最高：\(max | . * 100 | floor / 100)°C | 最低：\(min | . * 100 | floor / 100)°C | 平均：\(add / length | . * 100 | floor / 100)°C"
    '
fi

# 输出原始 JSON（可选）
# echo ""
# echo "📄 原始数据:"
# echo "$RESPONSE" | jq '.'
