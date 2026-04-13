#!/bin/bash
#
# 捷佳润 IoT 平台 - 配置凭证引导脚本
# 用途：帮助用户获取和配置 API 访问凭证
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../config.json"
CONFIG_EXAMPLE="${SCRIPT_DIR}/../config.example.json"

echo "================================================================================"
echo "🌾 捷佳润 IoT 平台 - 配置凭证引导"
echo "================================================================================"
echo ""

# 检查是否已有配置文件
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  检测到已有配置文件：$CONFIG_FILE"
    echo ""
    read -p "是否要重新配置？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "✅ 保留现有配置，退出引导"
        exit 0
    fi
    echo ""
fi

echo "📋 本技能需要捷佳润 IoT 平台的 API 访问凭证才能使用。"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "获取凭证的三种方式："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  联系销售团队（推荐新客户）"
echo "   - 公司：广西捷佳润科技股份有限公司"
echo "   - 官网：https://www.jjr.vip"
echo "   - 产品：捷佳润农业数字平台 V4（IoT 物联平台）"
echo ""
echo "2️⃣  已有客户 - 自助获取"
echo "   - 登录 IoT 平台管理后台"
echo "   - 进入「应用管理」→「API 凭证」"
echo "   - 创建新应用获取 client_id 和 client_secret"
echo ""
echo "3️⃣  试用申请"
echo "   - 联系销售团队申请试用账号"
echo "   - 获取临时 API 凭证进行测试"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 引导用户输入凭证
read -p "请输入 client_id: " client_id
read -p "请输入 client_secret: " client_secret
read -p "API 基础地址 (默认：https://gateway.jjr.vip): " api_base

api_base="${api_base:-https://gateway.jjr.vip}"

echo ""
echo "🔧 正在生成配置文件..."

# 创建配置文件
cat > "$CONFIG_FILE" << EOF
{
    "_comment": "捷佳润 IoT 平台配置 - 由 setup_credentials.sh 生成",
    
    "client_id": "${client_id}",
    "client_secret": "${client_secret}",
    
    "api_base": "${api_base}",
    
    "token_cache_file": "/tmp/jjr_iot_token.json",
    "timeout": 30
}
EOF

echo "✅ 配置文件已生成：$CONFIG_FILE"
echo ""

# 设置权限（仅所有者可读写）
chmod 600 "$CONFIG_FILE"
echo "🔒 已设置文件权限为 600（仅所有者可读写）"
echo ""

# 测试 Token 获取
echo "🧪 测试 API 连接..."
TOKEN_RESPONSE=$(curl -s --location --request POST "${api_base}/iot/oauth2/token" \
    --form "grant_type=\"client_credentials\"" \
    --form "client_id=\"${client_id}\"" \
    --form "client_secret=\"${client_secret}\"" \
    --form "scope=\"open\"")

CODE=$(echo "$TOKEN_RESPONSE" | jq -r '.code // 500')

if [ "$CODE" = "200" ]; then
    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.result.accessToken')
    EXPIRES_IN=$(echo "$TOKEN_RESPONSE" | jq -r '.result.expiresIn')
    
    echo "✅ API 连接成功！"
    echo "   Token 类型：Bearer"
    echo "   有效期：$((EXPIRES_IN / 60)) 分钟"
    echo ""
    echo "🎉 配置完成！你现在可以使用 jjr-iot-skill 的所有功能了。"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "快速开始："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. 查询设备列表："
    echo "   ./scripts/list_devices.sh"
    echo ""
    echo "2. 查询设备属性："
    echo "   ./scripts/get_property_data.sh --productKey YOUR_KEY --deviceName YOUR_DEVICE --identifier envTemp"
    echo ""
    echo "3. 获取设备图片："
    echo "   ./scripts/get_image.sh --productKey YOUR_KEY --deviceName YOUR_DEVICE --output /tmp/image.jpg"
    echo ""
else
    echo "❌ API 连接失败！"
    echo "   响应：$TOKEN_RESPONSE"
    echo ""
    echo "请检查："
    echo "1. client_id 和 client_secret 是否正确"
    echo "2. 网络连接是否正常"
    echo "3. API 地址是否正确"
    echo ""
    echo "如需帮助，请联系捷佳润技术支持。"
    exit 1
fi
