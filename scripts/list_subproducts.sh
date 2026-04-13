#!/bin/bash
#
# 捷佳润 IoT 平台 - 查询子产品列表脚本
# 用法：./list_subproducts.sh --productKey xxx [--page 1] [--size 10]
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
        --productKey)
            PRODUCT_KEY="$2"
            shift 2
            ;;
        --page)
            PAGE="$2"
            shift 2
            ;;
        --size)
            SIZE="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 --productKey PRODUCT_KEY [--page PAGE] [--size SIZE]"
            echo ""
            echo "必需参数:"
            echo "  --productKey  父产品 Key（网关产品 Key）"
            echo ""
            echo "可选参数:"
            echo "  --page        页码 (默认：1)"
            echo "  --size        每页数量 (默认：10)"
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
if [ -z "$PRODUCT_KEY" ]; then
    echo "❌ 缺少必需参数 --productKey"
    echo "请使用 --help 查看用法"
    exit 1
fi

# 获取 Token
TOKEN=$(/bin/bash "$(dirname "$0")/get_token.sh" --config "$CONFIG_FILE" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 构建查询参数
QUERY_PARAMS="productKey=${PRODUCT_KEY}&page=${PAGE}&size=${SIZE}"

# 查询子产品列表
RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/product/subList?${QUERY_PARAMS}" \
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

# 检查是否有数据
RECORD_COUNT=$(echo "$RESPONSE" | jq -r '.result.records | length')
if [ "$RECORD_COUNT" = "0" ] || [ "$RECORD_COUNT" = "null" ]; then
    echo "⚠️  未找到子产品"
    echo ""
    echo "💡 提示：确认父产品 Key ($PRODUCT_KEY) 是否正确，该产品下可能没有子产品"
    exit 0
fi

# 解析并显示子产品列表
echo "📦 子产品列表（父产品：$PRODUCT_KEY）:"
echo ""
echo "$RESPONSE" | jq -r '
.result.records[] |
"| \(.name) | \(.productKey) | \(.parentProductKey) | \(.type | if . == 2 then "子设备" else "其他" end) | \(.status | if . == 1 then "✅正常" else "❌停用" end) | \(.createTime) |"
' | column -t -s '|'

echo ""
echo "📊 汇总信息:"
echo "$RESPONSE" | jq -r '"   总子产品数：\(.result.total) | 当前页：\(.result.current)/\(.result.pages) | 每页：\(.result.size) 个"'
