---
name: jjr_iot
description: 捷佳润 IoT 平台技能，支持设备查询、属性数据、图片获取和定时任务
metadata:
  openclaw:
    os: ["linux", "darwin"]
    requires:
      bins: ["curl", "jq", "python3"]
tags: ["iot", "jjr", "agriculture", "sensors", "chinese"]
version: 1.0.0
---
# JJR IoT Skill - 捷佳润物联平台技能

> 🦐 捷佳润物联平台 IoT 数据查询与定时任务技能
>
> 规范上架中心：
> - **腾讯 SkillHub (国内镜像)**: [skillhub.cloud.tencent.com](https://skillhub.cloud.tencent.com/)
> - **ClawHub 官方 (国际版)**: [clawhub.ai](https://clawhub.ai/)

---

## 📋 技能描述

本技能提供捷佳润物联平台（JJR IoT Platform）的完整接口封装，支持：

- ✅ 设备列表查询
- ✅ 设备属性数据查询（温度、湿度等）
- ✅ 设备图片获取
- ✅ Cron 定时任务配置
- ✅ 多设备管理

---

## 🔧 配置要求

### 必需配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `client_id` | 物联平台 Client ID | 联系管理员或通过后台获取 |
| `client_secret` | 物联平台 Client Secret | 联系管理员或通过后台获取 |
| `api_base` | API 基础地址 | `https://gateway.jjr.vip`（默认） |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `token_cache_file` | Token 缓存文件路径 | `/tmp/jjr_iot_token.json` |
| `timeout` | 请求超时时间（秒） | `30` |

---

## 📦 安装方法

### 方式一：OpenClaw 直接安装（推荐）

直接对 OpenClaw 输入指令：
`安装 jjr iot skill` 或 `install jjr iot skill`

然后按提示将 `client_id` 和 `client_secret` 直接粘贴给 OpenClaw 即可完成自动配置。

### 方式二：Hub 平台安装

您可以前往官方 Hub 获取更多版本信息：
- **ClawHub 官方 (国际版)**: [clawhub.ai/skills/jjr-iot](https://clawhub.ai/skills/jjr-iot)
- **腾讯 SkillHub (国内镜像)**: [skillhub.cloud.tencent.com](https://skillhub.cloud.tencent.com/)

### 方式三：手动安装

```bash
# 克隆或复制到技能目录
cp -r jjr-iot-skill ~/.openclaw/workspace/skills/

# 配置认证信息
cp config.example.json config.json
# 编辑 config.json 填入你的 client_id, client_secret, product_key, device_name
```

---

## 🚀 快速开始

### 1. 获取 Token

```bash
./scripts/get_token.sh
```

### 2. 查询设备列表

```bash
./scripts/list_devices.sh --page 1 --size 10
```

### 3. 查询属性数据

```bash
./scripts/get_property_data.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --identifier envTemp \
  --startTime "2026-04-01 00:00:00" \
  --endTime "2026-04-13 00:00:00"
```

**提示：** 将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你的实际设备信息。

### 4. 获取设备图片

```bash
./scripts/get_image.sh \
  --productKey YOUR_PRODUCT_KEY \
  --deviceName YOUR_DEVICE_NAME \
  --output /tmp/latest_image.jpg
```

---

## 📖 API 接口

### 基础信息

| 项目 | 值 |
|------|-----|
| API 地址 | `https://gateway.jjr.vip/iot/` |
| Token 接口 | `POST /iot/oauth2/token` |
| Token 有效期 | 30 分钟 |
| 认证方式 | Bearer Token |

### 接口列表

#### 认证接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取 Token | POST | `/iot/oauth2/token` | 获取访问令牌（有效期 30 分钟） |

#### 设备管理接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 设备列表 | GET | `/iot/open/iot/device/list` | 查询设备列表（支持分页、按产品过滤） |
| 设备详情 | GET | `/iot/open/iot/device/detail` | 查询单个设备详情 |
| 设备配置 | GET | `/iot/open/iot/device/config` | 获取设备配置信息 |
| 编辑配置 | PUT | `/iot/open/iot/device/configEdit` | 编辑设备属性配置（按 identifier） |
| 配置下发 | POST | `/iot/open/iot/device/configSet` | 下发配置到设备（按 identifier） |
| 配置下发 | POST | `/iot/open/iot/device/config/push` | 下发配置到设备（批量） |

#### 产品管理接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 产品列表 | GET | `/iot/open/iot/product/list` | 查询产品列表（支持分页、按 productKey 过滤） |
| 产品详情 | GET | `/iot/open/iot/product/detail` | 查询单个产品详情 |

#### 数据查询接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 属性列表 | GET | `/iot/open/iot/device/property` | 获取设备属性列表（所有可用的属性标识符） |
| 属性数据 | GET | `/iot/open/iot/device/propertyData` | 查询属性历史数据（温度、湿度、图片等） |
| 属性下发 | POST | `/iot/open/iot/device/property/push` | 下发属性到设备 |
| 服务执行 | POST | `/iot/open/iot/device/service/invoke` | 调用设备服务 |
| 事件数据 | GET | `/iot/open/iot/device/eventData` | 查询设备事件历史 |

#### 子设备接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 子产品列表 | GET | `/iot/open/iot/product/subList` | 查询子产品列表（按 parentProductKey 过滤） |
| 子设备列表 | GET | `/iot/open/iot/device/subList` | 查询子设备列表 |

---

## ⏰ Cron 定时任务示例

### 每小时采集温度

```cron
0 * * * * /path/to/jjr-iot-skill/scripts/get_property_data.sh --productKey xxx --deviceName xxx --identifier envTemp
```

### 每天 9 点获取设备图片

```cron
0 9 * * * /path/to/jjr-iot-skill/scripts/get_image.sh --productKey xxx --deviceName xxx --output /tmp/daily_image.jpg
```

### 每 30 分钟推送数据到钉钉

```cron
*/30 * * * * /path/to/jjr-iot-skill/scripts/notify_dingtalk.sh --webhook xxx
```

---

## 📝 使用示例

### 示例 1：查询设备列表

```bash
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/list?page=1&size=10' \
  --header "Authorization: Bearer $TOKEN"
```

### 示例 2：查询温度数据

```bash
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/propertyData?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=envTemp&queryType=2&startTime=2026-04-01%2000:00:00&endTime=2026-04-13%2000:00:00' \
  --header "Authorization: Bearer $TOKEN"
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

### 示例 3：获取最新图片

```bash
# 先查询 imgUrl 属性
IMG_URL=$(./scripts/get_property_data.sh --identifier imgUrl --limit 1 | jq -r '.result[0].value')

# 下载图片
curl -L "$IMG_URL" -o /tmp/device_image.jpg
```

### 示例 4：查询产品列表

```bash
# 查询所有产品
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/product/list?page=1&size=50' \
  --header "Authorization: Bearer $TOKEN"

# 查询特定产品
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/product/list?productKey=YOUR_PRODUCT_KEY' \
  --header "Authorization: Bearer $TOKEN"

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "id": "xxx",
#         "name": "植物生长记录仪",
#         "productKey": "YOUR_PRODUCT_KEY",
#         "productSecret": "xxx",
#         "type": 0,
#         "createTime": "2026-01-20 14:21:57",
#         "status": 1
#       }
#     ],
#     "total": 23,
#     "size": 50,
#     "current": 1,
#     "pages": 1
#   }
# }
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 替换为你实际的产品 Key，返回示例中的敏感信息已脱敏。

### 示例 5：查询设备属性（完整参数）

```bash
# 查询温度数据
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/propertyData?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=envTemp&queryType=2&startTime=2026-04-01%2000:00:00&endTime=2026-04-13%2023:59:59' \
  --header "Authorization: Bearer $TOKEN"

# 查询图片 URL
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/propertyData?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=imgUrl&queryType=2&startTime=2026-04-01%2000:00:00&endTime=2026-04-13%2023:59:59' \
  --header "Authorization: Bearer $TOKEN"

# queryType 说明:
# 1 = 最新一条数据
# 2 = 时间范围内所有数据
# 3 = 聚合数据（按小时/天）
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

### 示例 6：查询子产品列表

```bash
# 查询网关设备的子产品
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/product/subList?productKey=YOUR_PARENT_PRODUCT_KEY&page=1&size=10' \
  --header "Authorization: Bearer $TOKEN"

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "id": "xxx",
#         "name": "网关子设备",
#         "productKey": "xxx",
#         "parentProductKey": "xxx",
#         "type": 2,
#         "createTime": "2025-07-30 23:01:55",
#         "status": 1
#       }
#     ],
#     "total": 5,
#     "size": 10,
#     "current": 1,
#     "pages": 1
#   }
# }
```

**注意：** 请将 `YOUR_PARENT_PRODUCT_KEY` 替换为你实际的父产品 Key。

### 示例 7：查询子设备列表

```bash
# 查询网关设备下的子设备
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/subList?deviceName=YOUR_PARENT_DEVICE_NAME&page=1&size=10' \
  --header "Authorization: Bearer $TOKEN"

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "id": "xxx",
#         "name": "测试子设备",
#         "deviceName": "xxx",
#         "productKey": "xxx",
#         "parentDeviceName": "xxx",
#         "type": 2,
#         "createTime": "2025-07-31 10:55:53",
#         "status": 1
#       }
#     ],
#     "total": 8,
#     "size": 10,
#     "current": 1,
#     "pages": 1
#   }
# }
```

**注意：** 请将 `YOUR_PARENT_DEVICE_NAME` 替换为你实际的父设备名称。

### 示例 8：查询子设备属性数据

```bash
# 查询子设备的温度数据（与主设备相同接口）
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/propertyData?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=envTemp&queryType=2&startTime=2026-04-01%2000:00:00&endTime=2026-04-13%2023:59:59' \
  --header "Authorization: Bearer $TOKEN"

# 💡 提示：子设备的数据查询接口与主设备相同，只需传入子设备的 productKey 和 deviceName
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的子设备信息。

### 示例 9：获取设备配置

```bash
# 获取设备配置信息
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/config?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME' \
  --header "Authorization: Bearer $TOKEN"

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "id": "xxx",
#         "configKey": "reportInterval",
#         "configValue": "300",
#         "configDesc": "数据上报间隔（秒）",
#         "updateTime": "2026-04-10 10:00:00"
#       }
#     ]
#   }
# }
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

### 示例 10：编辑设备配置

```bash
# 编辑设备属性配置（按 identifier）
curl --location --request PUT 'https://gateway.jjr.vip/iot/open/iot/device/configEdit?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=int&value=99' \
  --header "Authorization: Bearer $TOKEN"

# 参数说明:
# - productKey: 产品 Key
# - deviceName: 设备名称
# - identifier: 属性标识符（如：int, temp, hum 等）
# - value: 新的配置值

# 返回示例:
# {
#   "code": 200,
#   "message": "编辑成功",
#   "result": {
#     "success": true,
#     "updateTime": "2026-04-13 15:05:00"
#   }
# }

# 💡 提示：编辑配置后，需要使用配置下发功能将配置推送到设备才能生效
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

### 示例 11：配置下发到设备

```bash
# 方式一：下发单个属性（configSet 接口）
curl --location --request POST 'https://gateway.jjr.vip/iot/open/iot/device/configSet?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=int' \
  --header "Authorization: Bearer $TOKEN"

# 参数说明:
# - productKey: 产品 Key
# - deviceName: 设备名称
# - identifier: 属性标识符（下发该属性的当前配置值）

# 返回示例:
# {
#   "code": 200,
#   "message": "下发成功",
#   "result": {
#     "success": true,
#     "sendTime": "2026-04-13 15:10:00"
#   }
# }

# 💡 提示：configSet 接口下发的是该属性当前的配置值，设备收到后会立即应用
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

### 示例 12：批量配置下发

```bash
# 方式二：批量下发多个配置（config/push 接口）
curl --location --request POST 'https://gateway.jjr.vip/iot/open/iot/device/config/push' \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/json" \
  -d '{
    "productKey": "YOUR_PRODUCT_KEY",
    "deviceName": "YOUR_DEVICE_NAME",
    "configs": [
      {
        "configKey": "reportInterval",
        "configValue": "600"
      },
      {
        "configKey": "tempThreshold",
        "configValue": "45"
      }
    ]
  }'

# 💡 提示：config/push 接口可以一次性下发多个配置项，适合批量配置场景
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

### 示例 13：获取设备属性列表

```bash
# 获取设备支持的所有属性标识符
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/property?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME' \
  --header "Authorization: Bearer $TOKEN"

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "identifier": "envTemp",
#         "name": "环境温度",
#         "type": "float",
#         "unit": "°C",
#         "description": "设备采集的环境温度数据"
#       },
#       {
#         "identifier": "envHum",
#         "name": "环境湿度",
#         "type": "float",
#         "unit": "%RH",
#         "description": "设备采集的环境湿度数据"
#       }
#     ]
#   }
# }

# 💡 提示：使用此接口可以查询设备支持的所有属性，便于后续查询属性数据时确定 identifier 参数
```

**注意：** 请将 `YOUR_PRODUCT_KEY` 和 `YOUR_DEVICE_NAME` 替换为你实际的设备信息。

---

## 🔒 安全说明

1. **Token 管理**: Token 有效期 30 分钟，建议缓存复用
2. **密钥保护**: `client_secret` 请妥善保管，不要提交到版本控制
3. **权限控制**: 建议为不同应用创建不同的 client_id

---

## 🐛 故障排查

### 问题 1: Token 获取失败

```bash
# 检查网络
curl -v https://gateway.jjr.vip/iot/oauth2/token

# 检查配置
cat config.json
```

### 问题 2: 设备数据查询为空

- 确认 `productKey` 和 `deviceName` 正确
- 确认时间范围有数据
- 确认设备在线状态

### 问题 3: 图片无法下载

- 检查图片 URL 是否过期
- 检查 OSS 访问权限
- 尝试重新获取 imgUrl

---

## 📞 技术支持

- **官网:** [www.jjr.com.cn](http://www.jjr.com.cn)
- **邮箱:** [service@jjr.com.cn](mailto:service@jjr.com.cn)
- **文档:** [clawhub.ai/skills/jjr-iot](https://clawhub.ai/skills/jjr-iot)
- **Issue:** [github.com/janeXlab/jjr-iot-skill/issues](https://github.com/janeXlab/jjr-iot-skill/issues)

---

## 📄 许可证

MIT License

---

**版本:** 1.0.1  
**作者:** 捷佳润创新中心  
**最后更新:** 2026-04-13
