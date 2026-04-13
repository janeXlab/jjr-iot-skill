# JJR IoT Skill

> 🦐 捷佳润物联平台技能 - 让龙虾帮你管理 IoT 设备

---

## 🎯 功能特性

- ✅ **设备管理** - 查询设备列表、设备状态
- ✅ **数据查询** - 温度、湿度、图片等属性数据
- ✅ **定时任务** - 支持 Cron 定时采集和推送
- ✅ **简单易用** - 只需 AppID 和 Secret 即可使用

---

## 📦 安装

### 方式一：OpenClaw 直接安装（推荐）

直接对 OpenClaw 输入指令：
`安装 jjr iot skill` 或 `install jjr iot skill`

然后按提示将 `client_id` 和 `client_secret` 直接粘贴给 OpenClaw 即可完成自动配置。

### 方式二：手动安装

```bash
# 1. 复制技能到技能目录
cp -r jjr-iot-skill ~/.openclaw/workspace/skills/

# 2. 配置认证信息
cd ~/.openclaw/workspace/skills/jjr-iot-skill/
cp config.example.json config.json

# 3. 编辑配置文件
vim config.json
# 填入你的 client_id 和 client_secret
```

---

## 🚀 快速开始

### 1️⃣ 获取 Token

```bash
cd ~/.openclaw/workspace/skills/jjr-iot-skill/scripts/
./get_token.sh
```

### 2️⃣ 查询产品列表

```bash
# 查询所有产品
./list_products.sh --page 1 --size 10

# 查询特定产品
./list_products.sh --productKey a1Zk6COoaIW
```

### 3️⃣ 查询设备列表

```bash
./list_devices.sh --page 1 --size 10
```

### 4️⃣ 查询温度数据

```bash
./get_property_data.sh \
  --productKey a1Zk6COoaIW \
  --deviceName PR20250416100005 \
  --identifier envTemp \
  --startTime "2026-04-01 00:00:00" \
  --endTime "2026-04-13 00:00:00"
```

### 5️⃣ 编辑设备配置

```bash
# 编辑设备属性（如修改上报间隔）
./device_config.sh \
  --productKey 80NKGSWOKC \
  --deviceName N2APXOI160 \
  --edit int 99

# 下发配置到设备（立即生效）
./config_push.sh \
  --productKey 80NKGSWOKC \
  --deviceName N2APXOI160 \
  --configs "int=99"
```

### 6️⃣ 获取设备图片

```bash
./get_image.sh \
  --productKey a1Zk6COoaIW \
  --deviceName PR20250416100005 \
  --output /tmp/latest_image.jpg
```

---

## ⏰ Cron 定时任务

### 每小时采集温度

```bash
# 编辑 crontab
crontab -e

# 添加任务（每小时执行）
0 * * * * /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_property_data.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --identifier envTemp \
  --startTime "$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')" \
  --endTime "$(date '+%Y-%m-%d %H:%M:%S')" >> /var/log/jjr_temp.log 2>&1
```

### 每天 9 点获取设备图片

```bash
0 9 * * * /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/get_image.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --output /mnt/images/daily_$(date +\%Y\%m\%d).jpg
```

### 每 30 分钟推送数据到钉钉

```bash
*/30 * * * * /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts/notify_dingtalk.sh \
  --webhook YOUR_DINGTALK_WEBHOOK
```

---

## 📖 API 参考

### 基础信息

| 项目 | 值 |
|------|-----|
| API 地址 | `https://gateway.jjr.vip/iot/` |
| Token 接口 | `POST /iot/oauth2/token` |
| Token 有效期 | 30 分钟 |

### 接口列表

| 接口 | 路径 | 方法 |
|------|------|------|
| 获取 Token | `/iot/oauth2/token` | POST |
| 设备列表 | `/ultimate/open/iot/device/list` | GET |
| 产品列表 | `/ultimate/open/iot/product/list` | GET |
| 属性数据 | `/iot/open/iot/device/propertyData` | GET |

---

## 🔧 脚本说明

| 脚本 | 功能 | 参数 |
|------|------|------|
| `get_token.sh` | 获取访问 Token | `--config`, `--cache` |
| `list_products.sh` | 查询产品列表 | `--page`, `--size`, `--productKey` |
| `list_subproducts.sh` | 查询子产品列表 | `--productKey`, `--page`, `--size` |
| `list_devices.sh` | 查询设备列表 | `--page`, `--size`, `--productKey` |
| `list_subdevices.sh` | 查询子设备列表 | `--deviceName`, `--page`, `--size` |
| `list_properties.sh` | 查询设备属性列表 | `--productKey`, `--deviceName` |
| `device_config.sh` | 获取/更新/编辑设备配置 | `--productKey`, `--deviceName`, `--get/--update/--edit` |
| `config_push.sh` | 下发配置到设备 | `--productKey`, `--deviceName`, `--configs`, `--method` |
| `get_property_data.sh` | 查询属性数据 | `--productKey`, `--deviceName`, `--identifier`, `--startTime`, `--endTime` |
| `get_image.sh` | 获取设备图片 | `--productKey`, `--deviceName`, `--output`, `--all` |

---

## 🐛 常见问题

### Q: Token 获取失败？
A: 检查 `config.json` 中的 `client_id` 和 `client_secret` 是否正确。

### Q: 查询不到设备数据？
A: 确认 `productKey` 和 `deviceName` 正确，检查设备是否在线。

### Q: 图片下载失败？
A: 图片 URL 可能已过期，请重新获取最新的 imgUrl。

---

## 📞 支持

- **文档:** https://clawhub.ai/skills/jjr-iot
- **Issue:** https://github.com/jjr-agriculture/jjr-iot-skill/issues

---

## 📄 许可证

MIT License

---

**版本:** 1.0.1  
**更新日期:** 2026-04-13  
**作者:** 捷佳润创新中心  
**支持:** service@jjr.com.cn
