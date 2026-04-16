# JJR IoT Skill 使用示例

---

## 示例 1：查询设备列表

```bash
# 查询前 10 个设备
./scripts/list_devices.sh --page 1 --size 10

# 查询特定产品的设备
./scripts/list_devices.sh --productKey YOUR_PRODUCT_KEY --size 50

# 输出示例：
# ✅ 查询成功
#
# | 植物生长记录仪  | YOUR_DEVICE_NAME | YOUR_PRODUCT_KEY | 🟢在线  | 2026-01-20 14:21:57 |
# | 无线控阀终端    | YOUR_DEVICE_NAME_B | YOUR_PRODUCT_KEY_B | 🔴离线  | （示例日期） |
#
# 📊 汇总信息:
#    总设备数：164 | 当前页：1/17 | 每页：10 台
```

---

## 示例 2：查询温度数据

```bash
# 查询最近 7 天的温度数据
./scripts/get_property_data.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --identifier envTemp \
  --startTime "2026-04-06 00:00:00" \
  --endTime "2026-04-13 00:00:00"

# 输出示例：
# ✅ 查询成功
#
# 📋 查询条件:
#    产品 Key: YOUR_PRODUCT_KEY
#    设备名称：YOUR_DEVICE_NAME
#    属性标识：envTemp
#    时间范围：2026-04-06 00:00:00 ~ 2026-04-13 00:00:00
#
# 📊 数据条数：520
#
# | 2026-04-12 20:27:03 | 30.95 |
# | 2026-04-12 19:03:11 | 32.85 |
# | 2026-04-12 18:50:11 | 33.1  |
# ...
#
# 🌡️  温度统计:
#    最高：40.79°C | 最低：21.98°C | 平均：32.0°C
```

---

## 示例 3：获取设备图片

```bash
# 获取最新一张图片
./scripts/get_image.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --output /tmp/latest_image.jpg

# 输出示例：
# 🔍 查询图片列表...
# ✅ 找到 15 张图片
#
# 📷 下载最新图片...
#    拍摄时间：2026-04-13 09:25:18
#    保存路径：/tmp/latest_image.jpg
#
# ✅ 下载成功!
#    文件大小：1.2M
#
# 📄 图片路径：/tmp/latest_image.jpg
```

---

## 示例 4：Cron 定时任务

### 每小时采集温度并记录

```bash
# 编辑 crontab
crontab -e

# 添加任务
0 * * * * /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_property_data.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --identifier envTemp \
  --startTime "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')" \
  --endTime "$(date '+%Y-%m-%d %H:%M:%S')" \
  >> /var/log/jjr_temp_$(date +\%Y\%m\%d).log 2>&1
```

### 每天 9 点获取图片并发送到钉钉

```bash
# 创建发送脚本
cat > /home/cloud/scripts/send_daily_image.sh << 'EOF'
#!/bin/bash
IMAGE_PATH="/mnt/images/daily_$(date +\%Y\%m\%d).jpg"

# 获取图片
/home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_image.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --output "$IMAGE_PATH"

# 发送到钉钉
curl -X POST "https://api.dingtalk.com/v1.0/robot/groupMessages/send" \
  -H "Content-Type: application/json" \
  -H "x-acs-dingtalk-access-token: YOUR_TOKEN" \
  -d "{
    \"robotCode\": \"YOUR_ROBOT_CODE\",
    \"openConversationId\": \"YOUR_CONVERSATION_ID\",
    \"msgKey\": \"sampleImage\",
    \"msgParam\": \"{\\\"mediaId\\\":\\\"$(upload_to_dingtalk $IMAGE_PATH)\\\"}\"
  }"
EOF

chmod +x /home/cloud/scripts/send_daily_image.sh

# 配置 Cron
0 9 * * * /home/cloud/scripts/send_daily_image.sh
```

---

## 示例 5：批量查询多个设备

```bash
#!/bin/bash
# 批量查询多个设备的温度

DEVICES=(
  "YOUR_DEVICE_NAME"
  "YOUR_DEVICE_NAME_2"
  "YOUR_DEVICE_NAME_3"
)

for DEVICE in "${DEVICES[@]}"; do
  echo "=== 设备：$DEVICE ==="
  /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_property_data.sh \
    --productKey YOUR_PRODUCT_KEY \
    --deviceName "$DEVICE" \
    --identifier envTemp \
    --startTime "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')" \
    --endTime "$(date '+%Y-%m-%d %H:%M:%S')" \
    --limit 1
  echo ""
done
```

---

## 示例 6：温度告警

```bash
#!/bin/bash
# 温度超过 40°C 发送告警

THRESHOLD=40.0
WEBHOOK="YOUR_DINGTALK_WEBHOOK"

RESPONSE=$(/home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_property_data.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --identifier envTemp \
  --startTime "$(date -d '10 minutes ago' '+%Y-%m-%d %H:%M:%S')" \
  --endTime "$(date '+%Y-%m-%d %H:%M:%S')" \
  --limit 1)

TEMP=$(echo "$RESPONSE" | grep -o '| [0-9.]* |' | head -1 | grep -o '[0-9.]*')

if (( $(echo "$TEMP > $THRESHOLD" | bc -l) )); then
  curl "$WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{
      \"msgtype\": \"text\",
      \"text\": {
        \"content\": \"⚠️ 温度告警！\\n设备：YOUR_DEVICE_NAME\\n当前温度：${TEMP}°C\\n阈值：${THRESHOLD}°C\\n时间：$(date)\"
      }
    }"
fi
```

---

## 示例 7：生成日报

```bash
#!/bin/bash
# 生成每日温度报告

DEVICE="YOUR_DEVICE_NAME"
YESTERDAY=$(date -d 'yesterday' '+%Y-%m-%d')
START="${YESTERDAY} 00:00:00"
END="${YESTERDAY} 23:59:59"

RESPONSE=$(/home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_property_data.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName "$DEVICE" \
  --identifier envTemp \
  --startTime "$START" \
  --endTime "$END")

# 提取统计数据
MAX_TEMP=$(echo "$RESPONSE" | jq -r '.result | map(.value | tonumber) | max')
MIN_TEMP=$(echo "$RESPONSE" | jq -r '.result | map(.value | tonumber) | min')
AVG_TEMP=$(echo "$RESPONSE" | jq -r '.result | map(.value | tonumber) | add / length')

# 生成报告
cat << EOF
📊 每日温度报告 - ${YESTERDAY}

设备：${DEVICE}
最高温度：${MAX_TEMP}°C
最低温度：${MIN_TEMP}°C
平均温度：${AVG_TEMP}°C
数据点数：$(echo "$RESPONSE" | jq -r '.result | length')

生成时间：$(date)
EOF
```

---

**更多示例请访问:** https://skillhub.cloud.tencent.com/skills/jjr-iot-skill
