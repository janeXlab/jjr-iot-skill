# 📊 图表可视化报告生成指南

> 本目录提供多种图表报告生成脚本，支持不同样式、不同格式的报告输出

---

## 🔒 重要原则

**脚本必须是通用的，不能硬编码特定客户/作物信息！**

- ✅ 作物类型、设备信息、标准参数通过配置文件传入
- ✅ 不同客户使用不同的配置文件
- ✅ 脚本本身不包含任何客户敏感信息
- ❌ 禁止在脚本中写死"鹿茸菇"、"番茄"等特定作物名称
- ❌ 禁止在脚本中写死客户设备 ID、产品 Key

---

## 📁 脚本列表

| 脚本名称 | 用途 | 输出格式 | 说明 |
|----------|------|----------|------|
| `generate_report.py` | 基础报告生成 | HTML + PNG | 单图表，简单统计 |
| `generate_report_v2.py` | 进阶报告生成 | HTML + PNG | 多图表，带植物照片 |
| `generate_report_generic.py` | **通用报告生成** | HTML + PNG | **推荐**，参数通过配置文件传入 |
| `analyze_growth.py` | 生长数据分析 | PNG | 多子图，专业分析 |

---

## 🎨 图表样式

### 样式 1：单图表（generate_report.py）

**特点：**
- 单一折线图
- 温度/湿度/CO2/光照同图显示
- 标准化 Y 轴（0-1000）
- 适合快速预览

**适用场景：** 日常监测、快速汇报

---

### 样式 2：多图表（generate_report_v2.py）

**特点：**
- 多个子图垂直排列
- 每个指标独立 Y 轴
- 可添加植物生长照片
- 更清晰的数据对比

**适用场景：** 详细分析、周报/月报

---

### 样式 3：通用报告（generate_report_generic.py）⭐ 推荐

**特点：**
- 四要素同图对比
- 多 Y 轴显示真实数值
- **参数通过配置文件传入**（不同作物使用不同配置）
- 可配置标准参数范围
- 支持任意作物类型

**Y 轴配置（可配置）：**
- 左侧 Y 轴：温度（范围由配置指定）
- 左侧第二轴：湿度（范围由配置指定）
- 右侧 Y 轴：CO₂（范围由配置指定）
- 隐藏轴：光照（范围由配置指定）

**配置文件示例：**
```json
{
  "title": "🍅 温室番茄环境监测报告",
  "deviceName": "GREENHOUSE-A01",
  "cropType": "番茄（结果期）",
  "standards": {
    "temp": {"min": 20, "max": 28},
    "humidity": {"min": 60, "max": 80},
    "co2": {"min": 400, "max": 1000},
    "light": {"min": 20000, "max": 50000}
  }
}
```

**适用场景：** 所有作物、所有客户（通用）

---

### 📋 常见作物参数参考

| 作物 | 温度 (°C) | 湿度 (%) | CO₂ (ppm) | 光照 (lux) |
|------|-----------|----------|-----------|------------|
| 🍅 番茄 | 20-28 | 60-80 | 400-1000 | 20000-50000 |
| 🥒 黄瓜 | 18-30 | 70-90 | 400-1200 | 15000-40000 |
| 🍓 草莓 | 15-23 | 50-70 | 400-800 | 10000-30000 |
| 🌾 水稻 | 25-35 | 60-85 | 400-600 | 20000-60000 |
| 🌶️ 辣椒 | 20-30 | 60-75 | 400-1000 | 15000-40000 |
| 🥬 叶菜 | 15-25 | 65-80 | 400-800 | 10000-25000 |

**提示：** 根据作物生长阶段（苗期/生长期/开花期/结果期）调整参数

---

### 样式 4：专业分析（analyze_growth.py）

**特点：**
- 4-6 个子图网格布局
- 包含统计分析（平均值、标准差）
- 趋势线、拟合曲线
- 专业报告格式

**适用场景：** 科研分析、技术报告

---

## 📤 发送方式

### 方式 1：钉钉 AI 助理（推荐）

**原理：** OpenClaw dingtalk-connector 插件自动检测图片标记

**用法：**
```markdown
![报告描述](file:///完整路径/图片.png)
```

**示例：**
```markdown
![鹿茸菇环境监测报告](file:///home/cloud/.openclaw/workspace/reports/mushroom_report.png)
```

**优点：**
- ✅ 自动上传，无需手动调用 API
- ✅ 支持 Markdown 混排
- ✅ 简单可靠

**注意：** 必须使用 `file:///` 前缀

---

### 方式 2：钉钉 API 直接发送

**脚本：** `send_dingtalk_image.sh`

**用法：**
```bash
./send_dingtalk_image.sh \
  --image /path/to/report.png \
  --conversation-id cidXXX \
  --client-id XXX \
  --client-secret XXX
```

**参数说明：**
| 参数 | 必需 | 说明 |
|------|------|------|
| `--image` | ✅ | 图片文件路径 |
| `--conversation-id` | ✅ | 钉钉会话 ID |
| `--client-id` | ✅ | 机器人 Client ID（或使用环境变量 `DINGTALK_CLIENT_ID`） |
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
  --text "**监测时间：** 48 小时\\n**温度：** 正常\\n**湿度：** 正常"
```

**优点：**
- ✅ 可控制发送内容
- ✅ 支持定时任务
- ✅ 独立于 OpenClaw

---

### 方式 3：OpenClaw Cron + 脚本

**配置 crontab：**
```bash
# 每天 8:40 发送日报
40 8 * * * /path/to/generate_report_mushroom.py && \
  /path/to/send_dingtalk_image.sh --image /path/to/report.png ...
```

**优点：**
- ✅ 定时自动执行
- ✅ 无需人工干预

---

## 🔧 配置说明

### 钉钉机器人配置

**获取方式：**
1. 登录钉钉开放平台：https://open.dingtalk.com/
2. 创建"AI 助理"或"群机器人"
3. 获取 `clientId` 和 `clientSecret`

**权限要求：**
- 群消息发送权限
- 图片上传权限

---

### Python 依赖

```bash
# 必需依赖
pip3 install matplotlib pandas numpy

# 可选依赖（生成 PNG 截图）
pip3 install playwright
playwright install chromium
```

**注意：** 如果使用系统 Chrome，无需 `playwright install chromium`

---

## 📝 使用示例

### 示例 1：通用报告生成（推荐）⭐

**步骤 1：准备配置文件**

为不同客户/作物创建不同的配置文件：

```bash
# 客户 A - 鹿茸菇
cp config.report.example.json config.customerA_mushroom.json
# 编辑 config.customerA_mushroom.json，填入鹿茸菇的标准参数

# 客户 B - 番茄
cp config.report.example.json config.customerB_tomato.json
# 编辑 config.customerB_tomato.json，填入番茄的标准参数
```

**步骤 2：准备数据文件**

```bash
# 从 API 获取数据并保存
# （可以使用 get_property_data.sh 脚本）
```

**步骤 3：生成报告**

```bash
python3 generate_report_generic.py \
  --config config.customerA_mushroom.json \
  --data data_customerA.json \
  --output /home/cloud/.openclaw/workspace/reports/customerA_report.png
```

**输出：**
- HTML 报告：`/home/cloud/.openclaw/workspace/reports/customerA_report.html`
- PNG 图片：`/home/cloud/.openclaw/workspace/reports/customerA_report.png`

---

### 示例 2：常见作物配置示例

**番茄（结果期）：**
```bash
python3 generate_report_generic.py \
  --config config.tomato.example.json \
  --data tomato_data.json \
  --output tomato_report.png
```

**黄瓜（生长期）：**
```bash
python3 generate_report_generic.py \
  --config config.cucumber.example.json \
  --data cucumber_data.json \
  --output cucumber_report.png
```

**草莓（开花期）：**
```bash
python3 generate_report_generic.py \
  --config config.strawberry.example.json \
  --data strawberry_data.json \
  --output strawberry_report.png
```

**水稻（抽穗期）：**
```bash
python3 generate_report_generic.py \
  --config config.rice.example.json \
  --data rice_data.json \
  --output rice_report.png
```

---

### 示例 2：发送到钉钉

**方式 A（OpenClaw 自动）：**
```markdown
![鹿茸菇报告](file:///home/cloud/.openclaw/workspace/reports/mushroom_env_report.png)
```

**方式 B（脚本手动）：**
```bash
./send_dingtalk_image.sh \
  --image /home/cloud/.openclaw/workspace/reports/mushroom_env_report.png \
  --conversation-id cidXXXXXXXXXXXXXXXXXXXXXXXX== \
  --client-id YOUR_DINGTALK_CLIENT_ID \
  --client-secret YOUR_SECRET
```

---

### 示例 3：定时任务

```bash
# 编辑 crontab
crontab -e

# 添加每日报告任务
0 9 * * * cd /home/cloud/.openclaw/workspace/skills/jjr-iot-skill/scripts && \
  python3 generate_report_mushroom.py && \
  ./send_dingtalk_image.sh \
    --image /home/cloud/.openclaw/workspace/reports/mushroom_env_report.png \
    --conversation-id cidXXXXXXXXXXXXXXXXXXXXXXXX== \
    --client-id YOUR_DINGTALK_CLIENT_ID \
    --client-secret YOUR_SECRET
```

---

## 🐛 常见问题

### 问题 1：图片显示为空

**原因：** 路径格式不正确

**解决：**
- ✅ 使用 `file:///` 前缀
- ✅ 路径不要转义（不用反斜杠）
- ✅ 确保文件存在且可读

---

### 问题 2：钉钉 API 返回 "msgKey 无效"

**原因：** 机器人类型不匹配

**解决：**
- AI 助理使用 `markdown` 或 `text` msgKey
- 传统机器人使用 `picture` msgKey
- 检查机器人类型和权限

---

### 问题 3：matplotlib 中文乱码

**原因：** 默认字体不支持中文

**解决：**
```python
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
```

---

### 问题 4：Playwright 无法访问本地文件

**原因：** file:// 协议被阻止

**解决：**
- 使用本地 HTTP 服务器：`python3 -m http.server 8888`
- 访问：`http://localhost:8888/report.html`

---

## 📚 相关文档

- [SKILL.md](../SKILL.md) - 技能主文档
- [TOOLS.md](../../../TOOLS.md) - 本地配置说明
- [钉钉 API 文档](https://open.dingtalk.com/document/)

---

**更新日期：** 2026-04-16  
**作者：** 捷佳润创新中心  
**支持：** service@jjr.com.cn
