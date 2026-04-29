# JJR IoT Skill - 版本历史

## v1.3.1 (2026-04-29)

### 修复
- ✅ 统一版本号（SKILL.md、package.json、CHANGELOG.md）
- ✅ Chromium 路径改为可配置（环境变量 `CHROMIUM_PATH`）
- ✅ 邮箱修改

---

## v1.3.0 (2026-04-16)

### 文档与分发
- ✅ 官方入口统一为 [腾讯云 SkillHub](https://skillhub.cloud.tencent.com/skills/jjr-iot-skill)
- ✅ README / SKILL 链接与 API 说明修正；示例脱敏

### 安全
- ✅ `config.json` 不纳入版本库（`.gitignore` + 仅保留 `config.example.json`）
- ✅ 钉钉发送脚本取消硬编码 Client ID，支持 `--client-id` / `DINGTALK_CLIENT_ID`

### 功能（与既有能力一并归并为本版号）
- ✅ 图表可视化报告、钉钉消息发送（详见 SKILL.md）

---

## v1.2.0 (2026-04-16)

### 功能
- ✅ 新增服务执行接口 (`/iot/open/iot/device/serveSet`)
- ✅ 支持调用设备服务（传入服务标识符和输入参数）
- ✅ 新增 execute_service.sh 脚本
- ✅ 支持 JSON 格式输入参数

### 文档
- ✅ 更新 API 接口列表
- ✅ 新增示例 15：服务执行
- ✅ 更新版本号为 v1.2.0

---

## v1.1.0 (2026-04-16)

### 功能
- ✅ 新增设备服务接口 (`/iot/open/iot/device/serve`)
- ✅ 支持按产品 Key 筛选设备服务
- ✅ 支持按设备名称筛选设备服务
- ✅ 获取设备服务列表（服务 ID、名称、类型、状态等）

### 文档
- ✅ 更新 API 接口列表（SKILL.md）
- ✅ 新增示例 14：获取设备服务列表
- ✅ 更新版本号为 v1.1.0

---

## v1.0.0 (2026-04-13)

### 功能
- ✅ 设备列表查询
- ✅ 设备属性数据查询（温度、湿度等）
- ✅ 设备图片获取
- ✅ Cron 定时任务配置
- ✅ 多设备管理
- ✅ 配置下发（configSet/configPush）

### 安全
- ✅ 敏感信息脱敏（client_id/client_secret 使用占位符）
- ✅ 添加配置引导脚本（setup_credentials.sh）
- ✅ 区分内部用户和外部用户使用方式

### 文档
- ✅ 完整 API 接口文档（SKILL.md）
- ✅ 使用示例（README.md, examples/usage.md）
- ✅ YAML frontmatter（ClawHub 发布要求）
- ✅ .clawhubignore（排除敏感文件）

### 脚本（12 个）
1. get_token.sh - 获取 Token
2. list_devices.sh - 设备列表
3. list_products.sh - 产品列表
4. list_properties.sh - 属性列表
5. list_subdevices.sh - 子设备列表
6. list_subproducts.sh - 子产品列表
7. get_property_data.sh - 属性数据查询
8. get_image.sh - 设备图片获取
9. device_config.sh - 设备配置编辑
10. config_push.sh - 配置下发
11. generate_report.py - 可视化报告生成
12. setup_credentials.sh - 配置引导脚本

### v1.2.0 新增脚本
13. list_device_services.sh - 设备服务列表查询
14. execute_service.sh - 服务执行

---

**发布渠道：** 腾讯云 SkillHub、Clawhub（若可用）  
**打包文件:** jjr-iot-skill-v1.3.1.zip
