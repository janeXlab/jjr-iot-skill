#!/bin/bash
#
# 钉钉图片发送脚本
# 用法：./send_dingtalk_image.sh --image /path/to/image.png --conversation-id cidXXX --client-id XXX --client-secret XXX
#

set -e

# 默认配置（Client ID 请使用 --client-id 或环境变量 DINGTALK_CLIENT_ID，勿在仓库中硬编码）
CLIENT_ID="${DINGTALK_CLIENT_ID:-}"
CLIENT_SECRET=""
CONVERSATION_ID=""
IMAGE_PATH=""
MESSAGE_TYPE="markdown"
TITLE=""
TEXT=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE_PATH="$2"
            shift 2
            ;;
        --conversation-id)
            CONVERSATION_ID="$2"
            shift 2
            ;;
        --client-id)
            CLIENT_ID="$2"
            shift 2
            ;;
        --client-secret)
            CLIENT_SECRET="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --text)
            TEXT="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 --image /path/to/image.png --conversation-id cidXXX --client-id XXX --client-secret XXX"
            echo ""
            echo "选项:"
            echo "  --image          图片路径（必需）"
            echo "  --conversation-id 钉钉会话 ID（必需）"
            echo "  --client-id      钉钉机器人 Client ID（可选，也可用环境变量 DINGTALK_CLIENT_ID）"
            echo "  --client-secret  钉钉机器人 Client Secret（必需）"
            echo "  --title          Markdown 消息标题（可选）"
            echo "  --text           Markdown 消息内容（可选）"
            exit 0
            ;;
        *)
            echo "未知参数：$1"
            exit 1
            ;;
    esac
done

# 验证必需参数
if [ -z "$IMAGE_PATH" ]; then
    echo "❌ 错误：--image 参数必需"
    exit 1
fi

if [ -z "$CONVERSATION_ID" ]; then
    echo "❌ 错误：--conversation-id 参数必需"
    exit 1
fi

if [ -z "$CLIENT_ID" ]; then
    echo "❌ 错误：请设置钉钉 Client ID（--client-id 或环境变量 DINGTALK_CLIENT_ID）"
    exit 1
fi

if [ -z "$CLIENT_SECRET" ]; then
    echo "❌ 错误：--client-secret 参数必需"
    exit 1
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ 错误：图片文件不存在：$IMAGE_PATH"
    exit 1
fi

echo "📤 正在发送图片到钉钉..."
echo "   图片：$IMAGE_PATH"
echo "   会话：$CONVERSATION_ID"

# 步骤 1：获取 Token
echo "🔑 获取 Token..."
TOKEN_RESPONSE=$(curl -s "https://oapi.dingtalk.com/gettoken?appkey=${CLIENT_ID}&appsecret=${CLIENT_SECRET}")
TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败：$TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Token 获取成功"

# 步骤 2：上传图片到钉钉
echo "📤 上传图片..."
UPLOAD_RESPONSE=$(curl -s "https://oapi.dingtalk.com/media/upload?access_token=$TOKEN&type=image" \
  -X POST \
  -F "media=@$IMAGE_PATH")

MEDIA_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"media_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$MEDIA_ID" ]; then
    echo "❌ 上传图片失败：$UPLOAD_RESPONSE"
    exit 1
fi

echo "✅ 图片上传成功，MediaID: $MEDIA_ID"

# 步骤 3：发送图片消息
echo "📱 发送消息..."

if [ -n "$TITLE" ] && [ -n "$TEXT" ]; then
    # 发送 Markdown 消息（带图片链接）
    SEND_RESPONSE=$(curl -s -X POST "https://api.dingtalk.com/v1.0/robot/groupMessages/send" \
      -H "Content-Type: application/json" \
      -H "x-acs-dingtalk-access-token: $TOKEN" \
      -d "{
        \"robotCode\": \"$CLIENT_ID\",
        \"openConversationId\": \"$CONVERSATION_ID\",
        \"msgKey\": \"markdown\",
        \"msgParam\": \"{\\\"title\\\":\\\"$TITLE\\\",\\\"text\\\":\\\"$TEXT\\\"}\"
      }")
else
    # 发送图片消息
    SEND_RESPONSE=$(curl -s -X POST "https://api.dingtalk.com/v1.0/robot/groupMessages/send" \
      -H "Content-Type: application/json" \
      -H "x-acs-dingtalk-access-token: $TOKEN" \
      -d "{
        \"robotCode\": \"$CLIENT_ID\",
        \"openConversationId\": \"$CONVERSATION_ID\",
        \"msgKey\": \"picture\",
        \"msgParam\": \"{\\\"mediaId\\\":\\\"$MEDIA_ID\\\"}\"
      }")
fi

# 检查发送结果
if echo "$SEND_RESPONSE" | grep -q '"code":"invalidParameter"'; then
    echo "❌ 发送失败：$SEND_RESPONSE"
    exit 1
elif echo "$SEND_RESPONSE" | grep -q '"requestid"'; then
    echo "✅ 消息发送成功！"
    echo "   RequestID: $(echo "$SEND_RESPONSE" | grep -o '"requestid":"[^"]*"' | cut -d'"' -f4)"
else
    echo "⚠️  未知响应：$SEND_RESPONSE"
fi

echo "✅ 完成！"
