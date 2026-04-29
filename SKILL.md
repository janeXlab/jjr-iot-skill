---
name: jjr_iot
description: 捷佳润 IoT 平台技能，支持设备查询、属性数据、图片获取和定时任务
metadata:
  openclaw:
    os: ["linux", "darwin", "windows"]
    requires:
      bins: ["curl", "jq", "python3"]
tags: ["iot", "jjr", "agriculture", "sensors", "chinese"]
version: 1.3.1
---
# JJR IoT Skill - 捷佳润物联平台技能

> 🦐 捷佳润物联平台 IoT 数据查询与定时任务技能

---

## 📋 技能描述

本技能提供捷佳润物联平台（JJR IoT Platform）的完整接口封装，支持：

- ✅ 设备列表查询
- ✅ 设备属性数据查询（温度、湿度等）
- ✅ 设备图片获取
- ✅ Cron 定时任务配置
- ✅ 多设备管理
- ✅ **图表可视化报告生成**（HTML + PNG）
- ✅ **钉钉消息自动发送**（图片/Markdown）

---

## 🔧 配置要求

### 必需配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `client_id` | 物联平台 Client ID | 联系捷佳润销售获取（service@jjr.com.cn） |
| `client_secret` | 物联平台 Client Secret | 联系捷佳润销售获取（service@jjr.com.cn） |
| `api_base` | API 基础地址 | `https://gateway.jjr.vip`（默认） |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `token_cache_file` | Token 缓存文件路径 | `/tmp/jjr_iot_token.json` |
| `timeout` | 请求超时时间（秒） | `30` |

---

## 📦 安装方法

### 方式一：通过claw使用（推荐）

**已配置 API 凭证的用户**，可以直接对话查询设备数据。

直接对claw说：
```
查询设备列表
查看温度数据
获取设备图片
```

捷小码会自动调用技能包中的接口为你查询数据。

### 方式二：通过腾讯云 SkillHub 获取

技能页（当前版本说明与安装入口）：[jjr-iot-skill](https://skillhub.cloud.tencent.com/skills/jjr-iot-skill)

克隆或下载到本地技能目录后，运行配置向导：

```bash
cd ~/.openclaw/workspace/skills/jjr-iot/
./scripts/setup_credentials.sh
```

**还没有 API 凭证？** 脚本会提供捷佳润销售团队的联系方式。

### 方式三：通过 github 安装（若环境支持）
https://github.com/janeXlab/jjr-iot-skill
### 方式四：手动安装

```bash
# 克隆或复制到技能目录
cp -r jjr-iot-skill ~/.openclaw/workspace/skills/

# 配置认证信息（勿将含真实密钥的 config.json 提交到版本库）
cp config.example.json config.json
# 编辑 config.json 填入你的 client_id 和 client_secret
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
| 设备服务 | GET | `/iot/open/iot/device/serve` | 获取设备服务列表（按产品 Key/设备名称筛选） |
| 服务执行 | POST | `/iot/open/iot/device/serveSet` | 调用设备服务（传入服务标识符和输入参数） |
| **设备事件** | **GET** | **`/iot/open/iot/device/event`** | **获取设备事件类型列表（告警、故障等）** |
| **事件数据** | **GET** | **`/iot/open/iot/device/eventData`** | **查询设备事件历史数据（按事件类型/时间筛选）** |

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

### 示例 14：获取设备服务列表

```bash
# ⚠️ 注意：必须同时提供 productKey 和 deviceName
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/serve?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME' \
  --header "Authorization: Bearer $TOKEN"

# 按产品 Key + 设备名称筛选
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/serve?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME' \
  --header "Authorization: Bearer $TOKEN"

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": [
#     {
#       "id": "xxx",
#       "productKey": "YOUR_PRODUCT_KEY",
#       "type": 1,
#       "name": "测试服务",
#       "intro": "",
#       "identifier": "test_service",
#       "status": 1,
#       "input": [],
#       "output": "",
#       "serveLog": {...}
#     }
#   ]
# }

# 💡 提示：
# 1. 必须同时提供 productKey 和 deviceName
# 2. 返回 result 是数组，不是分页对象
# 3. 使用此接口可以查询设备支持的所有服务，便于后续调用服务执行接口
```

**注意：** 请将 `productKey` 和 `deviceName` 替换为你实际的产品 Key 和设备名称。

### 示例 15：服务执行

```bash
# 调用设备服务
# ⚠️ 注意：必须同时提供 productKey、deviceName、identifier 和 input 参数

curl --location --request POST 'https://gateway.jjr.vip/iot/open/iot/device/serveSet?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=hello&input={"x":"300","y":"300","z":"0"}' \
  --header "Authorization: Bearer $TOKEN"

# 参数说明:
# - productKey: 产品 Key（必填）
# - deviceName: 设备名称（必填）
# - identifier: 服务标识符（必填）- 从设备服务接口获取
# - input: 输入参数（必填）- JSON 字符串格式

# 💡 提示：
# 1. 先使用 /iot/open/iot/device/serve 接口查询设备支持的服务
# 2. 获取服务的 identifier（如：hello、test_service 等）
# 3. 根据服务要求构造 input 参数（JSON 格式）
# 4. input 参数需要 URL 编码

# 返回示例:
# {
#   "code": 200,
#   "message": "执行成功",
#   "result": {
#     "success": true,
#     "execTime": "2026-04-16 09:00:00"
#   }
# }
```

**注意：** 请将 `productKey`、`deviceName`、`identifier` 和 `input` 替换为你实际的服务信息。

### 示例 16：获取设备事件类型列表

```bash
# 查询设备支持的事件类型（告警、故障等）
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/event?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME' \
  --header "Authorization: Bearer $TOKEN"

# 参数说明:
# - productKey: 产品 Key（可选）
# - deviceName: 设备名称（可选）

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "id": "xxx",
#         "tenantId": "xxx",
#         "categoryId": "xxx",
#         "type": 1,
#         "name": "温度告警",
#         "productKey": "YOUR_PRODUCT_KEY",
#         "productSecret": "xxx",
#         "thumb": "",
#         "intro": "温度超过阈值时触发",
#         "isPass": 1,
#         "onlineType": "offline",
#         "positionType": 0,
#         "createTime": "2026-04-01 10:00:00",
#         "isOffice": "0",
#         "updateTime": "2026-04-01 10:00:00",
#         "status": 1
#       }
#     ],
#     "total": 5,
#     "size": 10,
#     "current": 1,
#     "pages": 1
#   }
# }

# 💡 提示：
# 1. type: 事件类型（1=告警，2=故障，3=维护等）
# 2. onlineType: 在线/离线触发（online=在线触发，offline=离线触发）
# 3. status: 事件状态（1=启用，0=禁用）
# 4. 使用此接口可以查询设备支持的所有事件类型，便于后续查询事件数据时确定 categoryId 参数
```

**注意：** 请将 `productKey` 和 `deviceName` 替换为你实际的设备信息。

### 示例 17：查询设备事件历史数据

```bash
# 查询设备事件历史（所有事件类型）
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/eventData?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&page=1&size=10' \
  --header "Authorization: Bearer $TOKEN"

# 查询特定事件类型的历史数据（使用 categoryId）
curl --location --request GET 'https://gateway.jjr.vip/iot/open/iot/device/eventData?productKey=YOUR_PRODUCT_KEY&deviceName=YOUR_DEVICE_NAME&identifier=test_event&page=1&size=10' \
  --header "Authorization: Bearer $TOKEN"

# 参数说明:
# - productKey: 产品 Key（可选）
# - deviceName: 设备名称（可选）
# - identifier: 事件标识符（可选）- 从设备事件接口获取的 categoryId
# - page: 页码（可选，默认：1）
# - size: 每页数量（可选，默认：10）

# 返回示例:
# {
#   "code": 200,
#   "message": "查询成功",
#   "result": {
#     "records": [
#       {
#         "id": "xxx",
#         "tenantId": "xxx",
#         "categoryId": "xxx",
#         "type": 1,
#         "name": "温度告警",
#         "productKey": "YOUR_PRODUCT_KEY",
#         "productSecret": "xxx",
#         "thumb": "",
#         "intro": "温度超过阈值时触发",
#         "isPass": 1,
#         "onlineType": "online",
#         "positionType": 0,
#         "createTime": "2026-04-16 10:30:00",
#         "isOffice": "0",
#         "updateTime": "2026-04-16 10:30:00",
#         "status": 1
#       }
#     ],
#     "total": 25,
#     "size": 10,
#     "current": 1,
#     "pages": 3
#   }
# }

# 💡 提示：
# 1. 先使用 /iot/open/iot/device/event 接口查询事件类型列表，获取 categoryId
# 2. 使用此接口查询特定事件类型的历史数据
# 3. 支持分页查询（page, size 参数）
# 4. createTime 是事件发生时间
# 5. type: 1=告警，2=故障，3=维护
# 6. onlineType: online=在线触发，offline=离线触发
```

**注意：** 请将 `productKey`、`deviceName` 和 `identifier` 替换为你实际的信息。

---

## 📊 图表可视化报告

### 🔒 安全原则

**脚本必须是通用的，不能硬编码特定客户/作物信息！**

- ✅ 作物类型、设备信息、标准参数通过配置文件传入
- ✅ 不同客户使用不同的配置文件
- ✅ 脚本本身不包含任何客户敏感信息
- ❌ 禁止在脚本中写死客户名称、作物类型、设备 ID

---

### 报告生成脚本

| 脚本 | 用途 | 输出格式 | 说明 |
|------|------|----------|------|
| `generate_report.py` | 基础报告 | HTML + PNG | 单图表 |
| `generate_report_v2.py` | 进阶报告 | HTML + PNG | 多图表 |
| `generate_report_generic.py` | **通用报告** ⭐ | HTML + PNG | **推荐**，参数通过配置传入 |
| `analyze_growth.py` | 专业分析 | PNG | 多子图 |

### 快速生成报告（通用方法）⭐

**步骤 1：创建配置文件**

```bash
# 复制示例配置
cp scripts/config.report.example.json config.my_crop.json

# 编辑配置文件，填入你的作物参数
# - title: 报告标题
# - cropType: 作物类型（如：鹿茸菇、番茄、草莓等）
# - standards: 标准参数范围（不同作物不同）
```

**步骤 2：生成报告**

```bash
python3 scripts/generate_report_generic.py \
  --config config.my_crop.json \
  --data data.json \
  --output /path/to/report.png
```

**输出：**
- HTML: `/path/to/report.html`
- PNG: `/path/to/report.png`

---

### 图表样式

**通用样式（generate_report_generic.py）：**
- 🌡️ 温度（左侧 Y 轴）：范围可配置
- 💧 湿度（左侧第二轴）：范围可配置
- 🌫️ CO₂（右侧 Y 轴）：范围可配置
- ☀️ 光照（隐藏轴）：范围可配置
- ✅ 多 Y 轴显示真实数值
- ✅ 支持任意作物类型
- ✅ 配置与代码分离，保护客户隐私

**详见：** `scripts/README_REPORTS.md`

---

## 📤 钉钉消息发送

### 方式 1：OpenClaw 自动上传（推荐）

**用法：** 在回复中直接使用图片标记

```markdown
![报告描述](file:///完整路径/图片.png)
```

**示例：**
```markdown
![鹿茸菇环境监测报告](file:///home/cloud/.openclaw/workspace/reports/mushroom_report.png)
```

**原理：** dingtalk-connector 插件自动检测 `file:///` 路径并上传图片

**优点：**
- ✅ 简单可靠，无需调用 API
- ✅ 支持 Markdown 混排
- ✅ OpenClaw 自动处理

---

### 方式 2：脚本手动发送

**脚本：** `scripts/send_dingtalk_image.sh`

**用法：**
```bash
./send_dingtalk_image.sh \
  --image /path/to/report.png \
  --conversation-id cidXXX \
  --client-id YOUR_DINGTALK_CLIENT_ID \
  --client-secret YOUR_SECRET
```

**参数说明：**
| 参数 | 必需 | 说明 |
|------|------|------|
| `--image` | ✅ | 图片文件路径 |
| `--conversation-id` | ✅ | 钉钉会话 ID |
| `--client-id` | ✅ | 机器人 Client ID（或预先 `export DINGTALK_CLIENT_ID=...`） |
| `--client-secret` | ✅ | 机器人 Client Secret |
| `--title` | ❌ | Markdown 标题 |
| `--text` | ❌ | Markdown 内容 |

**示例：**
```bash
./send_dingtalk_image.sh \
  --image /home/cloud/reports/mushroom_report.png \
  --conversation-id cidXXXXXXXXXXXXXXXXXXXXXXXX== \
  --client-id YOUR_DINGTALK_CLIENT_ID \
  --client-secret YOUR_SECRET \
  --title "🍄 鹿茸菇环境监测报告" \
  --text "**监测时间：** 48 小时\n**温度：** 正常"
```

---

### 方式 3：Cron 定时任务

**配置示例：**
```bash
# 每天 9 点自动生成并发送报告
0 9 * * * cd /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts && \
  python3 generate_report_mushroom.py && \
  ./send_dingtalk_image.sh \
    --image /home/cloud/.openclaw/workspace/reports/mushroom_env_report.png \
    --conversation-id cidXXXXXXXXXXXXXXXXXXXXXXXX== \
    --client-id YOUR_DINGTALK_CLIENT_ID \
    --client-secret YOUR_SECRET
```

---

## 🔒 安全说明

1. **Token 管理**: Token 有效期 30 分钟，建议缓存复用
2. **密钥保护**: `client_secret` 请妥善保管，不要提交到版本控制
3. **权限控制**: 建议为不同应用创建不同的 client_id
4. **钉钉密钥**: 钉钉 `clientSecret` 同样需要保密存储

---

## 🐛 故障排查

### 问题 1: Token 获取失败

```bash
# 检查网络
curl -v https://gateway.jjr.vip/iot/oauth2/token

# 检查配置（若不存在请先执行 cp config.example.json config.json 并填写凭证）
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

- **当前版本技能页（SkillHub）：** https://skillhub.cloud.tencent.com/skills/jjr-iot-skill
- **作者：** 捷佳润创新中心
- **支持：** service@jjr.com.cn
- **交流群:** 钉钉群（安装后获取邀请码）

---

## 📄 许可证

MIT License

---

**版本:** 1.3.1  
**创建日期:** 2026-04-13  
**最后更新:** 2026-04-16  
**更新内容:**  
- v1.3.0: 官方文档入口 [腾讯云 SkillHub](https://skillhub.cloud.tencent.com/skills/jjr-iot-skill)；图表可视化报告与钉钉消息发送；示例脱敏；`config.json` 不纳入版本库；钉钉脚本取消硬编码 Client ID  
- v1.2.0: 新增设备服务接口 (`/iot/open/iot/device/serve`)、服务执行接口 (`/iot/open/iot/device/serveSet`)
