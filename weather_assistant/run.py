#!/usr/bin/env python3
"""
Weather AI Assistant 启动脚本
检查依赖和配置后启动主程序
"""

import sys
import os
from dotenv import load_dotenv

def check_dependencies():
    """检查必要的依赖包"""
    required_packages = ['openai', 'python-dotenv', 'requests']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'openai':
                import openai
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'requests':
                import requests
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False

    return True

def check_config():
    """检查环境变量配置"""
    load_dotenv()

    required_vars = {
        'OPENAI_API_KEY': 'sk-',
        'AMAP_API_KEY': None  # 高德API密钥格式不固定
    }

    missing_configs = []

    for var_name, expected_prefix in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_configs.append(var_name)
        elif expected_prefix and not value.startswith(expected_prefix):
            print(f"❌ {var_name} 格式不正确，应以 '{expected_prefix}' 开头")
            missing_configs.append(var_name)

    if missing_configs:
        print("❌ 缺少或格式错误的配置:")
        for var in missing_configs:
            print(f"   - {var}")
        print("\n请检查 .env 文件中的配置")
        return False

    return True

def main():
    """主函数"""
    print("🌤️ Weather AI Assistant 启动检查...")

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 检查配置
    if not check_config():
        sys.exit(1)

    print("✅ 检查通过，启动 Weather AI Assistant...")
    print()

    # 导入并启动主程序
    try:
        from weather_ai_assistant import WeatherAssistant
        assistant = WeatherAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()