#!/bin/bash
#
# 捷佳润 IoT 平台 - 获取/更新设备配置脚本
# 用法：./device_config.sh --productKey xxx --deviceName xxx [--get|--update KEY VALUE]
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"
PRODUCT_KEY=""
DEVICE_NAME=""
ACTION="get"
CONFIG_KEY=""
CONFIG_VALUE=""

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
        --get)
            ACTION="get"
            shift
            ;;
        --update)
            ACTION="update"
            CONFIG_KEY="$2"
            CONFIG_VALUE="$3"
            shift 3
            ;;
        --edit)
            ACTION="edit"
            IDENTIFIER="$2"
            VALUE="$3"
            shift 3
            ;;
        --help)
            echo "用法：$0 --productKey PRODUCT_KEY --deviceName DEVICE_NAME [--get|--update KEY VALUE]"
            echo ""
            echo "必需参数:"
            echo "  --productKey  产品 Key"
            echo "  --deviceName  设备名称"
            echo ""
            echo "操作选项:"
            echo "  --get         获取设备配置（默认）"
            echo "  --update      更新设备配置（需要提供 KEY 和 VALUE）"
            echo "  --edit        编辑设备属性配置（需要提供 identifier 和 value）"
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

# 执行操作
if [ "$ACTION" = "get" ]; then
    # 获取配置
    echo "🔍 获取设备配置..."
    echo "   产品 Key: $PRODUCT_KEY"
    echo "   设备名称：$DEVICE_NAME"
    echo ""
    
    RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/device/config?productKey=${PRODUCT_KEY}&deviceName=${DEVICE_NAME}" \
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
        echo "⚠️  未找到配置信息"
        exit 0
    fi
    
    # 显示配置
    echo "✅ 查询成功"
    echo ""
    echo "📋 设备配置:"
    echo ""
    echo "$RESPONSE" | jq -r '
    .result.records[] |
    "| \(.configKey) | \(.configValue) | \(.configDesc // "无描述") | \(.updateTime // "未知") |"
    ' | column -t -s '|'
    
    echo ""
    echo "📊 配置总数：$RECORD_COUNT"
    
elif [ "$ACTION" = "edit" ]; then
    # 编辑配置
    if [ -z "$IDENTIFIER" ] || [ -z "$VALUE" ]; then
        echo "❌ 编辑操作需要提供 identifier 和 value"
        echo "用法：$0 --productKey $PRODUCT_KEY --deviceName $DEVICE_NAME --edit identifier value"
        exit 1
    fi
    
    echo "✏️  编辑设备配置..."
    echo "   产品 Key: $PRODUCT_KEY"
    echo "   设备名称：$DEVICE_NAME"
    echo "   属性标识：$IDENTIFIER"
    echo "   配置值：$VALUE"
    echo ""
    
    RESPONSE=$(curl -s --location --request PUT "${API_BASE}/iot/open/iot/device/configEdit?productKey=${PRODUCT_KEY}&deviceName=${DEVICE_NAME}&identifier=${IDENTIFIER}&value=${VALUE}" \
        --header "Authorization: Bearer ${TOKEN}")
    
    # 检查响应
    CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
    if [ "$CODE" != "200" ]; then
        echo "❌ 编辑失败：$RESPONSE"
        exit 1
    fi
    
    echo "✅ 配置编辑成功"
    echo ""
    echo "💡 提示：编辑配置后，需要使用配置下发功能将配置推送到设备才能生效"
    echo "   使用命令：./config_push.sh --productKey $PRODUCT_KEY --deviceName $DEVICE_NAME --configs \"$IDENTIFIER=$VALUE\""
    
elif [ "$ACTION" = "update" ]; then
    # 更新配置
    if [ -z "$CONFIG_KEY" ] || [ -z "$CONFIG_VALUE" ]; then
        echo "❌ 更新操作需要提供配置 KEY 和 VALUE"
        echo "用法：$0 --productKey $PRODUCT_KEY --deviceName $DEVICE_NAME --update KEY VALUE"
        exit 1
    fi
    
    echo "🔄 更新设备配置..."
    echo "   产品 Key: $PRODUCT_KEY"
    echo "   设备名称：$DEVICE_NAME"
    echo "   配置项：$CONFIG_KEY = $CONFIG_VALUE"
    echo ""
    
    # 构建 JSON 数据
    JSON_DATA=$(cat <<EOF
{
    "productKey": "$PRODUCT_KEY",
    "deviceName": "$DEVICE_NAME",
    "configKey": "$CONFIG_KEY",
    "configValue": "$CONFIG_VALUE"
}
EOF
)
    
    RESPONSE=$(curl -s --location --request PUT "${API_BASE}/iot/open/iot/device/config" \
        --header "Authorization: Bearer ${TOKEN}" \
        --header "Content-Type: application/json" \
        -d "$JSON_DATA")
    
    # 检查响应
    CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
    if [ "$CODE" != "200" ]; then
        echo "❌ 更新失败：$RESPONSE"
        exit 1
    fi
    
    echo "✅ 配置更新成功"
    echo ""
    echo "💡 提示：配置更新后，可能需要重启设备或等待下次上报才能生效"
    echo "   如需立即生效，请使用配置下发功能"
fi
