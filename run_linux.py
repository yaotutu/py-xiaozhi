#!/usr/bin/env python3
"""
Linux环境专用启动脚本
适用于嵌入式设备和无头Linux系统
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_linux_environment():
    """检查Linux环境兼容性"""
    print("=" * 50)
    print("🐧 小智AI Linux启动检查")
    print("=" * 50)
    
    # 系统信息
    print(f"系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # 设置环境变量以优化Linux运行
    env_vars = {
        "XIAOZHI_DISABLE_AUDIO": "0",  # 先尝试音频，失败时自动禁用
        "SDL_AUDIODRIVER": "pulse,alsa,dummy",  # SDL音频驱动优先级
        "PYGAME_HIDE_SUPPORT_PROMPT": "1",  # 隐藏pygame提示
    }
    
    # 检测是否为无头系统
    if not os.getenv("DISPLAY") and not os.path.exists("/dev/snd"):
        print("⚠️  检测到无头系统且无音频设备")
        env_vars["XIAOZHI_DISABLE_AUDIO"] = "1"
        
    # 设置环境变量
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"设置环境变量: {key}={value}")
    
    print("=" * 50)
    return True

def main():
    """主函数"""
    try:
        # 环境检查
        if not check_linux_environment():
            return 1
            
        # 导入并启动主程序
        print("🚀 启动小智AI CLI版本...")
        
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            
        # 导入主模块
        import main
        
        # 解析命令行参数
        sys.argv = [sys.argv[0]] + sys.argv[1:]  # 保留原始参数
        
        # 运行主程序
        return main.main() if hasattr(main, 'main') else 0
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
        return 0
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保在正确的conda环境中运行")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())