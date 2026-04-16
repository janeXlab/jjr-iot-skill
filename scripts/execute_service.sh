#!/bin/bash
#
# 服务执行 - 调用设备服务
# 用法:
#   ./execute_service.sh --productKey XXX --deviceName XXX --identifier XXX --input XXX
#
# 选项:
#   --productKey  产品 Key (必填)
#   --deviceName  设备名称 (必填)
#   --identifier  服务标识符 (必填) - 从设备服务接口获取
#   --input       输入参数 (必填) - JSON 字符串格式
#   --help        显示帮助信息
#
# 示例:
#   ./execute_service.sh --productKey YOUR_PRODUCT_KEY --deviceName YOUR_DEVICE_NAME --identifier hello --input '{"x":"300","y":"300","z":"0"}'
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.json"

# 默认值
PRODUCT_KEY=""
DEVICE_NAME=""
IDENTIFIER=""
INPUT=""

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
            echo "服务执行 - 调用设备服务"
            echo ""
            echo "用法: $0 --productKey XXX --deviceName XXX --identifier XXX --input XXX"
            echo ""
            echo "选项:"
            echo "  --productKey  产品 Key (必填)"
            echo "  --deviceName  设备名称 (必填)"
            echo "  --identifier  服务标识符 (必填) - 从设备服务接口获取"
            echo "  --input       输入参数 (必填) - JSON 字符串格式"
            echo "  --help        显示帮助信息"
            echo ""
            echo "示例:"
            echo "  $0 --productKey YOUR_PRODUCT_KEY --deviceName YOUR_DEVICE_NAME --identifier hello --input '{\"x\":\"300\",\"y\":\"300\",\"z\":\"0\"}'"
            echo ""
            echo "💡 提示:"
            echo "  1. 先使用 list_device_services.sh 查询设备支持的服务"
            echo "  2. 获取服务的 identifier (如：hello、test_service 等)"
            echo "  3. 根据服务要求构造 input 参数 (JSON 格式)"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 检查必需参数
if [ -z "$PRODUCT_KEY" ] || [ -z "$DEVICE_NAME" ] || [ -z "$IDENTIFIER" ] || [ -z "$INPUT" ]; then
    echo "❌ 错误：缺少必需参数"
    echo ""
    echo "必需参数:"
    echo "  --productKey  产品 Key"
    echo "  --deviceName  设备名称"
    echo "  --identifier  服务标识符"
    echo "  --input       输入参数 (JSON 格式)"
    echo ""
    echo "使用 --help 查看完整帮助"
    exit 1
fi

# 检查 jq 是否安装
if ! command -v jq &> /dev/null; then
    echo "错误：jq 未安装"
    echo "请运行：sudo apt-get install jq 或 brew install jq"
    exit 1
fi

# 获取 Token
TOKEN=$("$SCRIPT_DIR/get_token.sh" 2>/dev/null)
if [ -z "$TOKEN" ]; then
    echo "错误：无法获取 Token"
    echo "请检查 config.json 配置是否正确"
    exit 1
fi

# 构建 API 地址
API_BASE="https://gateway.jjr.vip/iot"
API_URL="$API_BASE/open/iot/device/serveSet?productKey=$PRODUCT_KEY&deviceName=$DEVICE_NAME&identifier=$IDENTIFIER&input=$INPUT"

# 发送请求
echo "📡 正在调用设备服务..." >&2
echo "  产品 Key: $PRODUCT_KEY" >&2
echo "  设备名称：$DEVICE_NAME" >&2
echo "  服务标识符：$IDENTIFIER" >&2
echo "  输入参数：$INPUT" >&2
echo ""

RESPONSE=$(curl --silent --location --request POST "$API_URL" \
  --header "Authorization: Bearer $TOKEN")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

if [ "$CODE" != "200" ]; then
    echo "❌ 服务执行失败：$MESSAGE"
    echo "响应：$RESPONSE" | jq .
    exit 1
fi

# 输出结果
echo "✅ 服务执行成功！"
echo ""
echo "$RESPONSE" | jq .

# 显示执行信息
if [ "$(echo "$RESPONSE" | jq -r '.result.success')" = "true" ]; then
    echo ""
    echo "=== 执行结果 ==="
    echo "状态：成功"
    EXEC_TIME=$(echo "$RESPONSE" | jq -r '.result.execTime // .result.sendTime // "未知"')
    echo "执行时间：$EXEC_TIME"
else
    echo ""
    echo "=== 执行结果 ==="
    echo "状态：失败"
fi
