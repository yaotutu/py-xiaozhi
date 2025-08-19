import argparse
import asyncio
import platform
import sys

from src.application import Application
from src.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def parse_args():
    """
    解析命令行参数.
    """
    parser = argparse.ArgumentParser(description="小智Ai客户端 (CLI版本)")
    parser.add_argument(
        "--protocol",
        choices=["mqtt", "websocket"],
        default="websocket",
        help="通信协议：mqtt 或 websocket",
    )
    parser.add_argument(
        "--skip-activation",
        action="store_true",
        help="跳过激活流程，直接启动应用（仅用于调试）",
    )
    return parser.parse_args()


async def handle_activation() -> bool:
    """处理设备激活流程，依赖已有事件循环.

    Returns:
        bool: 激活是否成功
    """
    try:
        from src.core.system_initializer import SystemInitializer

        logger.info("开始设备激活流程检查...")

        system_initializer = SystemInitializer()
        # CLI模式激活处理
        result = await system_initializer.handle_activation_process(mode="cli")
        success = bool(result.get("is_activated", False))
        logger.info(f"激活流程完成，结果: {success}")
        return success
    except Exception as e:
        logger.error(f"激活流程异常: {e}", exc_info=True)
        return False


async def start_app(protocol: str, skip_activation: bool) -> int:
    """
    启动CLI应用的入口（在已有事件循环中执行）.
    """
    logger.info("启动小智AI客户端 (CLI版本)")
    logger.info(f"运行在: {platform.system()} {platform.release()}")

    try:
        # 处理激活流程
        if not skip_activation:
            logger.info("开始设备激活流程...")
            activation_success = await handle_activation()
            if not activation_success:
                logger.error("设备激活失败，程序退出")
                return 1
        else:
            logger.warning("跳过激活流程（调试模式）")

        # 创建并启动应用程序
        logger.info("初始化应用程序...")
        app = Application.get_instance()
        logger.info("启动应用程序...")
        return await app.run(protocol=protocol)
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}", exc_info=True)
        return 1


def main():
    """主函数入口"""
    exit_code = 1
    try:
        args = parse_args()
        setup_logging()
        
        logger.info(f"小智AI CLI版本启动 - {platform.system()} {platform.release()}")

        # CLI模式使用标准asyncio事件循环
        exit_code = asyncio.run(
            start_app(args.protocol, args.skip_activation)
        )

    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        exit_code = 0
    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        logger.error("请检查依赖是否正确安装，或尝试重新安装requirements.txt")
        exit_code = 1
    except Exception as e:
        logger.error(f"程序异常退出: {e}", exc_info=True)
        if "audio" in str(e).lower() or "sound" in str(e).lower():
            logger.info("提示: 如果是音频相关问题，可以尝试设置环境变量 XIAOZHI_DISABLE_AUDIO=1")
        exit_code = 1
    finally:
        return exit_code

if __name__ == "__main__":
    sys.exit(main())
