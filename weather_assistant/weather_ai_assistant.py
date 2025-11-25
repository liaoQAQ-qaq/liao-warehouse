#!/usr/bin/env python3
"""
Weather AI Assistant
基于 DeepSeek API 的天气查询专用 AI 助手
"""

import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

class WeatherAssistant:
    def __init__(self):
        # 加载环境变量，覆盖已存在的
        load_dotenv(override=True)

        # 初始化 OpenAI 客户端（使用 DeepSeek API）
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )

        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")

        # 初始化高德地图天气API配置
        self.amap_api_key = os.getenv("AMAP_API_KEY")

        # 天气查询专用的系统提示词
        self.system_prompt = """你是一个专业的天气查询 AI 助手，擅长以下领域：

🌤️ 核心技能：
- 全球各地实时天气信息查询
- 天气预报和趋势分析
- 气象数据解读和专业术语解释
- 空气质量指数（AQI）查询和分析
- 极端天气预警和安全建议
- 季节性气候变化和穿衣建议
- 旅行天气规划和户外活动建议
- 农业气象和自然灾害预防

💡 回答风格：
- 提供准确、及时的天气信息
- 包含温度、湿度、风速等详细气象数据
- 解释天气现象时科学易懂
- 提供实用的出行和穿衣建议
- 关注天气变化对生活的影响

🌈 请用中文回答，保持友好、贴心的语调。如果遇到非天气相关问题，我会礼貌地引导回天气话题。

🔧 实时天气查询功能：
- 我可以连接到高德地图天气API获取实时天气数据
- 当用户询问具体城市的天气时，我会优先使用API获取准确信息
- 如果API不可用，我会基于训练数据提供参考信息"""

        # 对话历史
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def get_realtime_weather(self, city_code: str) -> dict:
        """获取实时天气数据"""
        if not self.amap_api_key:
            return {"error": "高德地图API配置不完整，请检查环境变量"}

        try:
            url = f"https://restapi.amap.com/v3/weather/weatherInfo"
            params = {
                'city': city_code,
                'key': self.amap_api_key,
                'extensions': 'base'  # 基础天气信息
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {"error": f"API请求失败，状态码: {response.status_code}"}

        except requests.exceptions.RequestException as e:
            return {"error": f"网络请求异常: {str(e)}"}
        except Exception as e:
            return {"error": f"获取天气数据失败: {str(e)}"}

    def format_weather_response(self, weather_data: dict, city_code: str) -> str:
        """格式化天气数据为友好的回复"""
        if "error" in weather_data:
            return f"❌ {weather_data['error']}"

        try:
            # 解析高德地图天气API的数据格式
            if weather_data.get("status") != "1":
                return f"❌ 天气查询失败: {weather_data.get('info', '未知错误')}"

            lives = weather_data.get("lives", [])
            if not lives:
                return "❌ 未获取到天气数据"

            weather_info = lives[0]  # 高德API返回的是数组，取第一个元素

            # 构建回复
            response = f"🌤️ **{weather_info.get('city', '未知地点')} 实时天气**\n\n"

            # 当前天气状况
            response += f"🌡️ **当前温度**: {weather_info.get('temperature', '--')}°C\n"
            response += f"💧 **相对湿度**: {weather_info.get('humidity', '--')}%\n"
            response += f"🌬️ **风向**: {weather_info.get('winddirection', '--')}级\n"
            response += f"💨 **风力**: {weather_info.get('windpower', '--')}级\n"
            response += f"🌫️ **空气质量**: {weather_info.get('weather', '--')}\n"
            response += f"📅 **报告时间**: {weather_info.get('reporttime', '--')}\n"

            # 添加生活建议
            temp = int(weather_info.get('temperature', 20))
            if temp <= 10:
                suggestion = "❄️ 天气寒冷，建议穿着厚外套、毛衣等保暖衣物，注意防寒。"
            elif temp <= 20:
                suggestion = "🍂 天气凉爽，建议穿着长袖、薄外套等。"
            elif temp <= 30:
                suggestion = "🌤️ 天气舒适，建议穿着轻便的春装或夏装。"
            else:
                suggestion = "🔥 天气炎热，建议穿着轻薄透气的衣物，注意防晒和补水。"

            response += f"\n💡 **穿衣建议**: {suggestion}"

            return response

        except Exception as e:
            return f"❌ 解析天气数据失败: {str(e)}"

    def display_welcome(self):
        """显示欢迎界面"""
        print("🤖" + "="*60)
        print("🌤️ Weather AI Assistant")
        print("💬 基于 DeepSeek API 的天气查询专用助手")
        print("🌡️ 输入 'help' 查看帮助，输入 'quit' 或 'exit' 退出")
        print("☀️ 让我开始为你查询天气信息！")
        print("🤖" + "="*60)

    def display_help(self):
        """显示帮助信息"""
        print("\n📚 Weather AI Assistant 帮助：")
        print("🌈 专门领域：")
        print("  • 实时天气查询和预报")
        print("  • 空气质量和气象数据")
        print("  • 极端天气预警")
        print("  • 旅行天气规划")
        print("  • 穿衣和出行建议")
        print("\n💡 使用技巧：")
        print("  • 提供具体的城市名称")
        print("  • 可以询问未来几天的天气预报")
        print("  • 询问空气质量或气象指数")
        print("  • 可以询问极端天气预警")

    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({"role": role, "content": content})

    def extract_city_from_input(self, user_input: str) -> str:
        """从用户输入中提取城市名称"""
        # 简单的城市名称提取逻辑
        weather_keywords = ['天气', '气温', '温度', '下雨', '晴天', '阴天', '雾霾', 'weather']

        # 检查是否包含天气相关关键词
        if not any(keyword in user_input for keyword in weather_keywords):
            return None

        # 常见城市映射表 (城市名 -> 高德地图adcode)
        city_mapping = {
            '北京': '110101',
            '上海': '310101',
            '广州': '440106',
            '深圳': '440304',
            '杭州': '330106',
            '成都': '510104',
            '重庆': '500101',
            '武汉': '420102',
            '西安': '610104',
            '天津': '120101',
            '南京': '320102',
            '苏州': '320508',
            '郑州': '410102',
            '长沙': '430104',
            '东莞': '441900',
            '沈阳': '210102',
            '青岛': '370202',
            '厦门': '350203'
        }

        # 检查用户输入中是否包含这些城市名
        for city, city_code in city_mapping.items():
            if city in user_input:
                return city_code

        return None

    def call_api(self, user_input: str) -> str:
        """调用 DeepSeek API，优先尝试实时天气查询"""
        try:
            # 首先检查是否为天气查询请求
            city_code = self.extract_city_from_input(user_input)

            if city_code:
                print("🔍 [检测到天气查询，正在获取实时数据...]")

                # 获取实时天气数据
                weather_data = self.get_realtime_weather(city_code)

                if "error" not in weather_data and weather_data.get("status") == "1":
                    # 成功获取实时天气数据，格式化后返回
                    weather_response = self.format_weather_response(weather_data, city_code)

                    # 添加到对话历史
                    self.add_message("user", user_input)
                    self.add_message("assistant", weather_response)

                    return weather_response
                else:
                    # API查询失败，使用AI回复并提示
                    print("⚠️ [实时天气API不可用，切换到AI回复模式]")
                    user_input += "\n\n[系统提示：由于实时天气API不可用，请基于你的训练数据提供天气参考信息]"

            # 添加用户消息
            self.add_message("user", user_input)

            # 调用 DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=2000,
                temperature=0.7,
                stream=False
            )

            assistant_response = response.choices[0].message.content

            # 添加助手回复到历史
            self.add_message("assistant", assistant_response)

            return assistant_response

        except Exception as e:
            error_msg = f"❌ API 调用出错: {str(e)}"
            print(error_msg)
            return error_msg

    def clear_history(self):
        """清空对话历史（保留系统提示）"""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        print("🧹 对话历史已清空")

    def run(self):
        """运行主循环"""
        self.display_welcome()

        while True:
            try:
                # 获取用户输入
                user_input = input("\n👨‍💻 你: ").strip()

                # 处理特殊命令
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 感谢使用 Weather AI Assistant！")
                    break
                elif user_input.lower() in ['help', '帮助']:
                    self.display_help()
                    continue
                elif user_input.lower() in ['clear', '清空']:
                    self.clear_history()
                    continue
                elif not user_input:
                    print("💡 请输入你的天气查询问题...")
                    continue

                # 调用 API 并显示结果
                print("\n🌤️ Weather Assistant: ", end="")
                response = self.call_api(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生未知错误: {str(e)}")


def main():
    """主函数"""
    try:
        # 检查 API 配置
        load_dotenv(override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        if not api_key or not api_key.startswith("sk-"):
            print("❌ API 密钥配置错误，请检查 .env 文件")
            return

        if not base_url:
            print("❌ Base URL 配置错误，请检查 .env 文件")
            return

        # 启动 Weather Assistant
        assistant = WeatherAssistant()
        assistant.run()

    except ImportError:
        print("❌ 缺少必要的依赖包，请运行：")
        print("pip install openai python-dotenv")
    except Exception as e:
        print(f"❌ 程序启动失败: {str(e)}")


if __name__ == "__main__":
    main()