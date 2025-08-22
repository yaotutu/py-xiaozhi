import asyncio
import logging
import sys
from typing import Callable, Optional

from src.display.base_display import BaseDisplay


class SimpleCliDisplay(BaseDisplay):
    """简化版CLI显示 - 只显示状态和日志，不追求美观"""
    
    def __init__(self):
        super().__init__()
        self.running = True
        
        # 状态信息
        self.status = "未连接"
        self.connected = False
        
        # 回调函数
        self.auto_callback = None
        self.abort_callback = None
        self.send_text_callback = None
        self.mode_callback = None
        self.press_callback = None
        self.release_callback = None
        
        # 异步队列用于处理命令
        self.command_queue = asyncio.Queue()
        
        # 不拦截日志，让日志正常输出到控制台
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志格式"""
        # 获取根日志记录器
        root = logging.getLogger()
        root.setLevel(logging.INFO)  # 显示 INFO 及以上级别的日志
        
        # 创建控制台处理器
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # 清除现有处理器并添加新的
        root.handlers.clear()
        root.addHandler(handler)
    
    async def set_callbacks(
        self,
        press_callback: Optional[Callable] = None,
        release_callback: Optional[Callable] = None,
        mode_callback: Optional[Callable] = None,
        auto_callback: Optional[Callable] = None,
        abort_callback: Optional[Callable] = None,
        send_text_callback: Optional[Callable] = None,
    ):
        """设置回调函数"""
        self.auto_callback = auto_callback
        self.abort_callback = abort_callback
        self.send_text_callback = send_text_callback
        self.mode_callback = mode_callback
        self.press_callback = press_callback
        self.release_callback = release_callback
    
    async def update_button_status(self, text: str):
        """更新按钮状态"""
        # 直接打印状态
        print(f"[按钮] {text}")
    
    async def update_status(self, status: str, connected: bool):
        """更新连接状态"""
        self.status = status
        self.connected = connected
        print(f"[状态] {status} | 连接: {'是' if connected else '否'}")
    
    async def update_text(self, text: str):
        """更新文本显示"""
        if text and text.strip():
            print(f"[AI] {text.strip()}")
    
    async def update_emotion(self, emotion_name: str):
        """更新表情"""
        # 简单显示表情状态
        if emotion_name:
            print(f"[表情] {emotion_name}")
    
    async def start(self):
        """启动CLI显示"""
        print("\n=== AI语音助手启动 ===")
        print("命令: b=开始录音 | e=停止录音 | r=自动模式 | x=打断 | q=退出 | h=帮助")
        print("直接输入文字发送消息\n")
        
        # 启动命令处理任务
        command_task = asyncio.create_task(self._command_processor())
        input_task = asyncio.create_task(self._input_loop())
        
        try:
            await asyncio.gather(command_task, input_task)
        except KeyboardInterrupt:
            await self.close()
    
    async def _command_processor(self):
        """处理命令队列"""
        while self.running:
            try:
                command = await asyncio.wait_for(
                    self.command_queue.get(), 
                    timeout=1.0
                )
                if asyncio.iscoroutinefunction(command):
                    await command()
                else:
                    command()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"命令处理错误: {e}")
    
    async def _input_loop(self):
        """输入循环"""
        try:
            while self.running:
                # 使用简单的输入提示
                cmd = await asyncio.to_thread(input, "> ")
                await self._handle_command(cmd.strip())
        except (KeyboardInterrupt, EOFError):
            await self.close()
        except asyncio.CancelledError:
            pass
    
    async def _handle_command(self, cmd: str):
        """处理用户命令"""
        cmd_lower = cmd.lower()
        
        if cmd_lower == "q":
            await self.close()
        elif cmd_lower == "h":
            print("\n命令说明:")
            print("  b - 开始录音")
            print("  e - 停止录音")
            print("  r - 切换自动模式")
            print("  x - 打断当前操作")
            print("  q - 退出程序")
            print("  h - 显示帮助")
            print("  其他文字 - 发送文本消息\n")
        elif cmd_lower == "r":
            if self.auto_callback:
                print("[操作] 切换自动模式")
                await self.command_queue.put(self.auto_callback)
        elif cmd_lower == "b":
            if self.press_callback:
                print("[操作] 开始录音...")
                await self.command_queue.put(self.press_callback)
        elif cmd_lower == "e":
            if self.release_callback:
                print("[操作] 停止录音")
                await self.command_queue.put(self.release_callback)
        elif cmd_lower == "x":
            if self.abort_callback:
                print("[操作] 打断当前操作")
                await self.command_queue.put(self.abort_callback)
        elif cmd:  # 非空文本
            if self.send_text_callback:
                print(f"[发送] {cmd}")
                await self.send_text_callback(cmd)
    
    async def close(self):
        """关闭CLI显示"""
        self.running = False
        print("\n正在关闭应用...")
    
    async def toggle_mode(self):
        """CLI模式下的模式切换"""
        self.logger.debug("切换模式")
    
    async def toggle_window_visibility(self):
        """CLI模式下的窗口切换"""
        self.logger.debug("CLI模式不支持窗口切换")