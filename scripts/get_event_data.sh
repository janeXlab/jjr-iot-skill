#!/bin/bash
#
# 查询设备事件历史数据
# 用法：./get_event_data.sh --productKey XXX --deviceName XXX [--identifier XXX] [--page 1 --size 10]
#

set -e

# 默认配置
PRODUCT_KEY=""
DEVICE_NAME=""
IDENTIFIER=""
PAGE=1
SIZE=10
START_TIME=""
END_TIME=""

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
        --page)
            PAGE="$2"
            shift 2
            ;;
        --size)
            SIZE="$2"
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
        --help)
            echo "用法：$0 --productKey XXX --deviceName XXX [--identifier XXX] [--page 1 --size 10]"
            echo ""
            echo "选项:"
            echo "  --productKey    产品 Key（可选）"
            echo "  --deviceName    设备名称（可选）"
            echo "  --identifier    事件标识符（可选）- 从 list_device_events.sh 获取"
            echo "  --page          页码（默认：1）"
            echo "  --size          每页数量（默认：10）"
            echo "  --startTime     开始时间（可选，格式：YYYY-MM-DD HH:MM:SS）"
            echo "  --endTime       结束时间（可选，格式：YYYY-MM-DD HH:MM:SS）"
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
CONFIG_FILE="$SCRIPT_DIR/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在：$CONFIG_FILE"
    echo "请先运行：./setup_credentials.sh"
    exit 1
fi

# 读取配置
CLIENT_ID=$(jq -r '.client_id' "$CONFIG_FILE")
CLIENT_SECRET=$(jq -r '.client_secret' "$CONFIG_FILE")
API_BASE=$(jq -r '.api_base // "https://gateway.jjr.vip"' "$CONFIG_FILE")

# 获取 Token
TOKEN=$("$SCRIPT_DIR/get_token.sh" | tail -n 1)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 构建查询参数
QUERY_PARAMS="page=$PAGE&size=$SIZE"

if [ -n "$PRODUCT_KEY" ]; then
    QUERY_PARAMS="$QUERY_PARAMS&productKey=$PRODUCT_KEY"
fi

if [ -n "$DEVICE_NAME" ]; then
    QUERY_PARAMS="$QUERY_PARAMS&deviceName=$DEVICE_NAME"
fi

if [ -n "$IDENTIFIER" ]; then
    QUERY_PARAMS="$QUERY_PARAMS&identifier=$IDENTIFIER"
fi

if [ -n "$START_TIME" ]; then
    QUERY_PARAMS="$QUERY_PARAMS&startTime=$START_TIME"
fi

if [ -n "$END_TIME" ]; then
    QUERY_PARAMS="$QUERY_PARAMS&endTime=$END_TIME"
fi

# 查询事件数据
echo "🔍 查询设备事件历史数据..."
if [ -n "$PRODUCT_KEY" ]; then
    echo "   产品 Key: $PRODUCT_KEY"
fi
if [ -n "$DEVICE_NAME" ]; then
    echo "   设备名称：$DEVICE_NAME"
fi
if [ -n "$IDENTIFIER" ]; then
    echo "   事件标识符：$IDENTIFIER"
fi
if [ -n "$START_TIME" ]; then
    echo "   开始时间：$START_TIME"
fi
if [ -n "$END_TIME" ]; then
    echo "   结束时间：$END_TIME"
fi
echo "   页码：$PAGE, 每页：$SIZE"

RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/device/eventData?$QUERY_PARAMS" \
  --header "Authorization: Bearer $TOKEN")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // 0')

if [ "$CODE" != "200" ]; then
    echo "❌ 查询失败：$RESPONSE"
    exit 1
fi

# 输出结果
echo "✅ 查询成功！"
echo ""

# 解析结果
TOTAL=$(echo "$RESPONSE" | jq -r '.result.total // 0')
RECORDS=$(echo "$RESPONSE" | jq -r '.result.records // []')
PAGES=$(echo "$RESPONSE" | jq -r '.result.pages // 0')

echo "📊 共找到 $TOTAL 条事件记录，共 $PAGES 页"
echo ""

if [ "$TOTAL" -eq 0 ]; then
    echo "💡 暂无事件数据"
    exit 0
fi

# 格式化输出
echo "$RECORDS" | jq -r '.[] | "📌 [\(.createTime)] \(.name)\n   事件 ID: \(.id)\n   类型：\(.type == 1 | if . then "🚨 告警" elif .type == 2 then "⚠️ 故障" else "🔧 维护" end)\n   触发：\(.onlineType == "online" | if . then "在线" else "离线" end)\n   产品：\(.productKey)\n   说明：\(.intro // "无")\n"'

# 分页提示
if [ "$PAGE" -lt "$PAGES" ]; then
    echo "💡 还有更多数据，使用 --page $((PAGE + 1)) 查看下一页"
fi
