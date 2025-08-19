#!/bin/bash
# Linux环境配置脚本

echo "🐧 配置小智AI Linux运行环境"
echo "=================================="

# 检查系统类型
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此脚本仅适用于Linux系统"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 设置权限
chmod +x run_linux.py
chmod +x main.py

# 创建启动别名
echo "# 小智AI快捷启动" >> ~/.bashrc
echo "alias xiaozhi='cd $(pwd) && python3 run_linux.py'" >> ~/.bashrc

# 安装系统依赖（如果需要）
echo "📦 检查系统依赖..."

# ALSA音频支持（可选）
if command -v apt-get &> /dev/null; then
    echo "检测到apt包管理器，建议安装音频支持："
    echo "sudo apt-get update"
    echo "sudo apt-get install -y alsa-utils pulseaudio pulseaudio-utils"
elif command -v yum &> /dev/null; then
    echo "检测到yum包管理器，建议安装音频支持："
    echo "sudo yum install -y alsa-utils pulseaudio pulseaudio-utils"
fi

echo ""
echo "✅ Linux环境配置完成！"
echo ""
echo "🚀 启动方法："
echo "1. 直接运行: python3 run_linux.py"
echo "2. 或使用别名: source ~/.bashrc && xiaozhi"
echo "3. 无音频模式: XIAOZHI_DISABLE_AUDIO=1 python3 run_linux.py"
echo ""
echo "📝 注意事项："
echo "- 首次运行可能需要设备激活"
echo "- 如遇到音频问题，程序会自动禁用音频功能"
echo "- 在无头系统上建议使用 --skip-activation 参数"