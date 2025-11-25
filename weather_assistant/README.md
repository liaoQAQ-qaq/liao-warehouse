# Weather AI Assistant

基于 DeepSeek API 和高德地图天气API的智能天气查询助手

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的API密钥：

```env
# DeepSeek API配置
OPENAI_API_KEY=sk-your-deepseek-api-key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat

# 高德地图天气API配置
AMAP_API_KEY=your-amap-api-key
```

### 3. 运行程序

```bash
python weather_ai_assistant.py
```

## 📱 功能特性

### 🔥 主要功能
- **实时天气查询** - 通过高德地图API获取准确的实时天气数据
- **智能城市识别** - 自动识别用户输入中的城市名称
- **智能对话** - 基于DeepSeek AI的天气相关问答
- **生活建议** - 根据天气提供穿衣和出行建议
- **API降级** - 实时API失败时自动切换到AI回复模式

### 🏙️ 支持的城市
- **华北**: 北京、天津、西安、郑州
- **华东**: 上海、杭州、南京、苏州、青岛、厦门
- **华南**: 广州、深圳、东莞
- **华中**: 武汉、长沙
- **西南**: 成都、重庆
- **东北**: 沈阳

## 🛠️ 项目结构

```
weather_assistant/
├── weather_ai_assistant.py    # 主程序文件
├── test_weather_assistant.py  # 测试脚本
├── requirements.txt          # 依赖包列表
├── .env                     # 环境变量配置
├── .env.example             # 环境变量模板
└── README.md               # 项目说明
```

## 🎯 使用方法

### 示例查询：
```
• 今天北京的天气怎么样？
• 上海天气如何？
• 广州现在的气温
• 深圳空气质量指数
```

### 特殊命令：
- `help` 或 `帮助` - 显示帮助信息
- `clear` 或 `清空` - 清空对话历史
- `quit`、`exit` 或 `退出` - 退出程序

## 🔧 API集成

### 高德地图天气API
- **接口地址**: `https://restapi.amap.com/v3/weather/weatherInfo`
- **返回数据**: 温度、湿度、风向、风力、天气状况等
- **更新频率**: 实时

### DeepSeek AI API
- **功能**: 智能对话和天气相关知识问答
- **用途**: API失败时的降级服务和复杂天气咨询

## 🧪 运行测试

```bash
python test_weather_assistant.py
```

## 📞 获取API密钥

### DeepSeek API
1. 访问 [DeepSeek官网](https://platform.deepseek.com/)
2. 注册账号并获取API密钥

### 高德地图API
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册开发者账号
3. 创建应用并获取Web服务API密钥

## 🌟 特色功能

- **智能路由**: 优先使用实时API，确保数据准确性
- **自动降级**: API不可用时无缝切换到AI模式
- **城市识别**: 智能识别用户输入中的城市名称
- **友好显示**: 结构化的天气信息展示
- **生活建议**: 基于天气的实用建议

---

🌤️ **享受智能的天气查询服务！**