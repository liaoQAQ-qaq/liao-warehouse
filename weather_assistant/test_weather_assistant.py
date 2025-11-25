#!/usr/bin/env python3
"""
测试 Weather AI Assistant 的基本功能
"""

import sys
import os
from dotenv import load_dotenv
from weather_ai_assistant import WeatherAssistant

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试 Weather AI Assistant 基本功能...")

    try:
        # 初始化助手
        assistant = WeatherAssistant()
        print("✅ 助手初始化成功")

        # 测试 API 配置
        load_dotenv(override=True)
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        if api_key and api_key.startswith("sk-"):
            print("✅ API 密钥配置正确")
        else:
            print("❌ API 密钥配置错误")
            return False

        if base_url:
            print("✅ Base URL 配置正确")
        else:
            print("❌ Base URL 配置错误")
            return False

        # 测试单个 API 调用
        print("\n🌤️ 测试 API 调用...")
        test_question = "今天北京的天气怎么样？"
        response = assistant.call_api(test_question)

        if response and not response.startswith("❌"):
            print("✅ API 调用成功")
            print(f"📝 回复预览: {response[:100]}...")
            return True
        else:
            print("❌ API 调用失败")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 所有测试通过！Weather AI Assistant 可以正常使用。")
        print("💡 运行 'python weather_ai_assistant.py' 开始使用")
    else:
        print("\n❌ 测试失败，请检查配置")
        sys.exit(1)