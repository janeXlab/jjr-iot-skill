#!/bin/bash
#
# 捷佳润 IoT 平台 - 配置下发脚本
# 用法：./config_push.sh --productKey xxx --deviceName xxx --configs "KEY1=VALUE1" [--method configSet|configPush]
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"
PRODUCT_KEY=""
DEVICE_NAME=""
CONFIGS=""
CONFIG_FILE_PATH=""
METHOD="configPush"

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
        --configs)
            CONFIGS="$2"
            shift 2
            ;;
        --config-file)
            CONFIG_FILE_PATH="$2"
            shift 2
            ;;
        --method)
            METHOD="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 --productKey PRODUCT_KEY --deviceName DEVICE_NAME --configs \"KEY1=VALUE1\" [--method configSet|configPush]"
            echo ""
            echo "必需参数:"
            echo "  --productKey  产品 Key"
            echo "  --deviceName  设备名称"
            echo "  --configs     配置项"
            echo ""
            echo "可选参数:"
            echo "  --method      下发方法：configSet（单个属性）或 configPush（批量），默认 configPush"
            echo "  --config-file 从文件读取配置（JSON 格式）"
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
if [ -z "$PRODUCT_KEY" ] || [ -z "$DEVICE_NAME" ] || ([ -z "$CONFIGS" ] && [ -z "$CONFIG_FILE_PATH" ]); then
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

# 执行下发
if [ "$METHOD" = "configSet" ]; then
    # configSet 接口 - 下发单个属性
    if [ -z "$CONFIGS" ]; then
        echo "❌ configSet 方法需要提供 identifier"
        echo "用法：$0 --productKey $PRODUCT_KEY --deviceName $DEVICE_NAME --configs identifier --method configSet"
        exit 1
    fi
    
    echo "📤 下发配置到设备（configSet - 单个属性）..."
    echo "   产品 Key: $PRODUCT_KEY"
    echo "   设备名称：$DEVICE_NAME"
    echo "   属性标识：$CONFIGS"
    echo ""
    
    RESPONSE=$(curl -s --location --request POST "${API_BASE}/iot/open/iot/device/configSet?productKey=${PRODUCT_KEY}&deviceName=${DEVICE_NAME}&identifier=${CONFIGS}" \
        --header "Authorization: Bearer ${TOKEN}")
    
else
    # config/push 接口 - 批量下发配置
    # 构建配置数组
    if [ -n "$CONFIG_FILE_PATH" ]; then
        # 从文件读取
        if [ ! -f "$CONFIG_FILE_PATH" ]; then
            echo "❌ 配置文件不存在：$CONFIG_FILE_PATH"
            exit 1
        fi
        CONFIGS_JSON=$(cat "$CONFIG_FILE_PATH")
    else
        # 从命令行解析
        CONFIGS_JSON="["
        FIRST=true
        IFS=',' read -ra PAIRS <<< "$CONFIGS"
        for PAIR in "${PAIRS[@]}"; do
            KEY=$(echo "$PAIR" | cut -d'=' -f1)
            VALUE=$(echo "$PAIR" | cut -d'=' -f2-)
            
            if [ "$FIRST" = true ]; then
                FIRST=false
            else
                CONFIGS_JSON+=","
            fi
            CONFIGS_JSON+="{\"configKey\":\"$KEY\",\"configValue\":\"$VALUE\"}"
        done
        CONFIGS_JSON+="]"
    fi
    
    echo "📤 下发配置到设备（configPush - 批量）..."
    echo "   产品 Key: $PRODUCT_KEY"
    echo "   设备名称：$DEVICE_NAME"
    echo "   配置项：$CONFIGS"
    echo ""
    
    # 构建 JSON 数据
    JSON_DATA=$(cat <<EOF
{
    "productKey": "$PRODUCT_KEY",
    "deviceName": "$DEVICE_NAME",
    "configs": $CONFIGS_JSON
}
EOF
)
    
    # 下发配置
    RESPONSE=$(curl -s --location --request POST "${API_BASE}/iot/open/iot/device/config/push" \
        --header "Authorization: Bearer ${TOKEN}" \
        --header "Content-Type: application/json" \
        -d "$JSON_DATA")
fi

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
if [ "$CODE" != "200" ]; then
    echo "❌ 下发失败：$RESPONSE"
    exit 1
fi

echo "✅ 配置下发成功"
echo ""
echo "💡 提示：设备会立即收到并应用新配置"
echo "   建议等待 1-2 分钟后查询设备状态确认配置生效"
