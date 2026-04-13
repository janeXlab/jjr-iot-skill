#!/bin/bash
#
# 捷佳润 IoT 平台 - 获取设备图片脚本
# 用法：./get_image.sh --productKey xxx --deviceName xxx --output xxx.jpg
#

set -e

# 默认配置
CONFIG_FILE="${CONFIG_FILE:-../config.json}"
API_BASE="${API_BASE:-https://gateway.jjr.vip}"
OUTPUT_DIR="/tmp/jjr_iot_images"

# 参数
PRODUCT_KEY=""
DEVICE_NAME=""
OUTPUT=""
LATEST_ONLY=true
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
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --all)
            LATEST_ONLY=false
            shift
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
            echo "用法：$0 --productKey XXX --deviceName XXX [--output FILE.jpg]"
            echo ""
            echo "必需参数:"
            echo "  --productKey   产品 Key"
            echo "  --deviceName   设备名称"
            echo ""
            echo "可选参数:"
            echo "  --output       输出文件路径 (默认：/tmp/jjr_iot_images/最新图片.jpg)"
            echo "  --output-dir   输出目录 (默认：/tmp/jjr_iot_images)"
            echo "  --all          下载所有图片 (默认只下载最新一张)"
            echo "  --startTime    开始时间 (与 --all 配合使用)"
            echo "  --endTime      结束时间 (与 --all 配合使用)"
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
if [ -z "$PRODUCT_KEY" ] || [ -z "$DEVICE_NAME" ]; then
    echo "❌ 缺少必需参数"
    echo "请使用 --help 查看用法"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 获取 Token
TOKEN=$(/bin/bash "$(dirname "$0")/get_token.sh" --config "$CONFIG_FILE" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

# 如果没有指定时间范围，默认查询最近 7 天
if [ -z "$START_TIME" ]; then
    START_TIME=$(date -d "7 days ago" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -v-7d "+%Y-%m-%d %H:%M:%S")
fi
if [ -z "$END_TIME" ]; then
    END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
fi

# URL 编码时间参数
START_TIME_ENCODED=$(echo "$START_TIME" | sed 's/ /%20/g')
END_TIME_ENCODED=$(echo "$END_TIME" | sed 's/ /%20/g')

# 查询 imgUrl 属性
QUERY_PARAMS="productKey=${PRODUCT_KEY}&deviceName=${DEVICE_NAME}&identifier=imgUrl&queryType=2&startTime=${START_TIME_ENCODED}&endTime=${END_TIME_ENCODED}"

echo "🔍 查询图片列表..."
RESPONSE=$(curl -s --location --request GET "${API_BASE}/iot/open/iot/device/propertyData?${QUERY_PARAMS}" \
    --header "Authorization: Bearer ${TOKEN}")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // 500')
if [ "$CODE" != "200" ]; then
    echo "❌ 查询失败：$RESPONSE"
    exit 1
fi

# 检查是否有数据
RECORD_COUNT=$(echo "$RESPONSE" | jq -r '.result | length')
if [ "$RECORD_COUNT" = "0" ] || [ "$RECORD_COUNT" = "null" ]; then
    echo "⚠️  未找到图片数据"
    exit 0
fi

echo "✅ 找到 $RECORD_COUNT 张图片"
echo ""

# 获取图片 URL
if [ "$LATEST_ONLY" = true ]; then
    # 只获取最新一张
    IMG_URL=$(echo "$RESPONSE" | jq -r '.result[0].value')
    IMG_TIME=$(echo "$RESPONSE" | jq -r '.result[0].time')
    
    if [ -z "$OUTPUT" ]; then
        OUTPUT="${OUTPUT_DIR}/${DEVICE_NAME}_latest.jpg"
    fi
    
    echo "📷 下载最新图片..."
    echo "   拍摄时间：$IMG_TIME"
    echo "   保存路径：$OUTPUT"
    echo ""
    
    curl -L "$IMG_URL" -o "$OUTPUT" 2>/dev/null
    
    if [ -f "$OUTPUT" ]; then
        FILE_SIZE=$(ls -lh "$OUTPUT" | awk '{print $5}')
        echo "✅ 下载成功!"
        echo "   文件大小：$FILE_SIZE"
        echo ""
        echo "📄 图片路径：$OUTPUT"
    else
        echo "❌ 下载失败"
        exit 1
    fi
else
    # 下载所有图片
    echo "📷 下载所有图片到：$OUTPUT_DIR"
    echo ""
    
    DOWNLOADED=0
    FAILED=0
    
    echo "$RESPONSE" | jq -r '.result[] | "\(.time)|\(.value)"' | while IFS='|' read -r TIME URL; do
        # 从 URL 提取文件名
        FILENAME=$(basename "$URL")
        # 用时间重命名文件
        SAFE_TIME=$(echo "$TIME" | sed 's/[: ]/_/g')
        OUTPUT_FILE="${OUTPUT_DIR}/${DEVICE_NAME}_${SAFE_TIME}.jpg"
        
        echo "   下载：$TIME -> $OUTPUT_FILE"
        curl -L "$URL" -o "$OUTPUT_FILE" 2>/dev/null
        
        if [ -f "$OUTPUT_FILE" ]; then
            DOWNLOADED=$((DOWNLOADED + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    done
    
    echo ""
    echo "✅ 下载完成"
fi
