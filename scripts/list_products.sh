#!/bin/bash
#
# 捷佳润 IoT 平台 - 查询产品列表脚本
# 用法：./list_products.sh [--page 1] [--size 10] [--productKey xxx]
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"
PAGE=1
SIZE=10
PRODUCT_KEY=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --page)
            PAGE="$2"
            shift 2
            ;;
        --size)
            SIZE="$2"
            shift 2
            ;;
        --productKey)
            PRODUCT_KEY="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 [--page PAGE] [--size SIZE] [--productKey PRODUCT_KEY]"
            echo ""
            echo "选项:"
            echo "  --page        页码 (默认：1)"
            echo "  --size        每页数量 (默认：10)"
            echo "  --productKey  产品 Key (可选，用于查询特定产品)"
            echo "  --help        显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            exit 1
            ;;
    esac
done

# 获取 Token
TOKEN=$(/bin/bash "$(dirname "$0")/get_token.sh" --config "$CONFIG_FILE" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 构建查询参数
QUERY_PARAMS="page=${PAGE}&size=${SIZE}"
if [ -n "$PRODUCT_KEY" ]; then
    QUERY_PARAMS="${QUERY_PARAMS}&productKey=${PRODUCT_KEY}"
fi

# 查询产品列表
RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/product/list?${QUERY_PARAMS}" \
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

# 解析并显示产品列表
echo "📦 产品列表:"
echo ""
echo "$RESPONSE" | jq -r '
.result.records[] |
"| \(.name) | \(.productKey) | \(.type | if . == 0 then "直连设备" elif . == 1 then "网关" else "子设备" end) | \(.status | if . == 1 then "✅正常" else "❌停用" end) | \(.createTime) |"
' | column -t -s '|'

echo ""
echo "📊 汇总信息:"
echo "$RESPONSE" | jq -r '"   总产品数：\(.result.total) | 当前页：\(.result.current)/\(.result.pages) | 每页：\(.result.size) 个"'
