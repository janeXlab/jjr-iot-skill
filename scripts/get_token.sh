#!/bin/bash
#
# 捷佳润 IoT 平台 - 获取 Token 脚本
# 用法：./get_token.sh [--config CONFIG_FILE]
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
TOKEN_CACHE_FILE="${TOKEN_CACHE_FILE:-/tmp/jjr_iot_token.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --cache)
            TOKEN_CACHE_FILE="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 [--config CONFIG_FILE] [--cache CACHE_FILE]"
            echo ""
            echo "选项:"
            echo "  --config    配置文件路径 (默认：../config.json)"
            echo "  --cache     Token 缓存文件路径 (默认：/tmp/jjr_iot_token.json)"
            echo "  --help      显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            exit 1
            ;;
    esac
done

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在：$CONFIG_FILE"
    echo "请复制 config.example.json 为 config.json 并填入配置信息"
    exit 1
fi

# 读取配置
CLIENT_ID=$(jq -r '.client_id' "$CONFIG_FILE")
CLIENT_SECRET=$(jq -r '.client_secret' "$CONFIG_FILE")

if [ "$CLIENT_ID" = "null" ] || [ "$CLIENT_SECRET" = "null" ]; then
    echo "❌ 配置不完整，请检查 config.json"
    exit 1
fi

# 检查缓存的 Token 是否有效
if [ -f "$TOKEN_CACHE_FILE" ]; then
    CACHE_TIME=$(jq -r '.cache_time // 0' "$TOKEN_CACHE_FILE")
    EXPIRES_IN=$(jq -r '.expires_in // 0' "$TOKEN_CACHE_FILE")
    CURRENT_TIME=$(date +%s)
    
    # 提前 5 分钟刷新
    if [ $((CURRENT_TIME - CACHE_TIME)) -lt $((EXPIRES_IN - 300)) ]; then
        echo "✅ 使用缓存的 Token"
        jq -r '.access_token' "$TOKEN_CACHE_FILE"
        exit 0
    fi
fi

echo "🔄 获取新 Token..."

# 请求 Token
RESPONSE=$(curl -s --location --request POST "${API_BASE}/iot/oauth2/token" \
    --form "grant_type=\"client_credentials\"" \
    --form "client_id=\"${CLIENT_ID}\"" \
    --form "client_secret=\"${CLIENT_SECRET}\"" \
    --form "scope=\"open\"")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
if [ "$CODE" != "200" ]; then
    echo "❌ Token 获取失败：$RESPONSE"
    exit 1
fi

# 提取 Token 信息
ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.result.accessToken')
EXPIRES_IN=$(echo "$RESPONSE" | jq -r '.result.expiresIn')
TOKEN_TYPE=$(echo "$RESPONSE" | jq -r '.result.tokenType')

# 保存缓存
cat > "$TOKEN_CACHE_FILE" << EOF
{
    "access_token": "$ACCESS_TOKEN",
    "token_type": "$TOKEN_TYPE",
    "expires_in": $EXPIRES_IN,
    "cache_time": $(date +%s),
    "expire_time": $(($(date +%s) + EXPIRES_IN))
}
EOF

echo "✅ Token 获取成功"
echo "   类型：$TOKEN_TYPE"
echo "   有效期：$((EXPIRES_IN / 60)) 分钟"
echo ""
echo "$ACCESS_TOKEN"
