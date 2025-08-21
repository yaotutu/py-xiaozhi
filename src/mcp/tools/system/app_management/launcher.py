"""Linux应用程序启动器."""

import asyncio
from typing import Any, Dict, Optional

from src.utils.logging_config import get_logger

from .utils import find_best_matching_app

logger = get_logger(__name__)


async def launch_application(args: Dict[str, Any]) -> bool:
    """启动应用程序.

    Args:
        args: 包含应用程序名称的参数字典
            - app_name: 应用程序名称

    Returns:
        bool: 启动是否成功
    """
    try:
        app_name = args["app_name"]
        logger.info(f"[AppLauncher] 尝试启动应用程序: {app_name}")

        # 首先尝试通过扫描找到精确匹配的应用程序
        matched_app = await _find_matching_application(app_name)
        if matched_app:
            logger.info(
                f"[AppLauncher] 找到匹配的应用程序: {matched_app.get('display_name', matched_app.get('name', ''))}"
            )
            # 使用匹配的应用启动
            success = await _launch_matched_app(matched_app, app_name)
        else:
            # 如果没有找到匹配，使用原来的方法
            logger.info(f"[AppLauncher] 未找到精确匹配，使用原始名称: {app_name}")
            success = await _launch_by_name(app_name)

        if success:
            logger.info(f"[AppLauncher] 成功启动应用程序: {app_name}")
        else:
            logger.warning(f"[AppLauncher] 启动应用程序失败: {app_name}")

        return success

    except Exception as e:
        logger.error(f"[AppLauncher] 启动应用程序出错: {e}")
        return False


async def _find_matching_application(app_name: str) -> Optional[Dict[str, Any]]:
    """查找匹配的应用程序.

    Args:
        app_name: 应用程序名称

    Returns:
        Optional[Dict[str, Any]]: 匹配的应用程序信息，未找到返回None
    """
    try:
        from .scanner import scan_applications

        # 扫描系统中的应用程序
        apps = await scan_applications()
        if not apps:
            return None

        # 查找最佳匹配
        return find_best_matching_app(app_name, apps)

    except Exception as e:
        logger.error(f"[AppLauncher] 查找应用程序失败: {e}")
        return None


async def _launch_matched_app(
    matched_app: Dict[str, Any], original_name: str
) -> bool:
    """启动匹配的应用程序.

    Args:
        matched_app: 匹配的应用程序信息
        original_name: 原始应用名称

    Returns:
        bool: 启动是否成功
    """
    try:
        app_path = matched_app.get("path", matched_app.get("name", original_name))
        
        # Linux应用程序启动
        return await _launch_by_name(app_path)

    except Exception as e:
        logger.error(f"[AppLauncher] 启动匹配应用失败: {e}")
        return False


async def _launch_by_name(app_name: str) -> bool:
    """根据名称启动应用程序.

    Args:
        app_name: 应用程序名称或路径

    Returns:
        bool: 启动是否成功
    """
    try:
        from .linux.launcher import launch_application

        return await asyncio.to_thread(launch_application, app_name)

    except Exception as e:
        logger.error(f"[AppLauncher] 启动应用程序失败: {e}")
        return False


def get_system_launcher():
    """获取Linux启动器模块.

    Returns:
        Linux启动器模块
    """
    from .linux import launcher

    return launcher