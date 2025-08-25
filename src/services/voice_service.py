# 语音服务
# 提供简单的录音控制接口

import asyncio
from typing import Optional, Callable


class VoiceService:
    # 初始化语音服务
    def __init__(self):
        # 当前是否在录音
        self.is_recording = False
        
        # 回调函数
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_stop: Optional[Callable] = None
        self.on_text_received: Optional[Callable] = None
        self.on_status_changed: Optional[Callable] = None
        
        # 应用实例引用
        self.app = None
        
    # 设置应用实例
    def set_app(self, app):
        self.app = app
        
    # 开始录音
    # 对应CLI中的'b'键
    async def start_recording(self):
        if self.is_recording:
            return False
            
        self.is_recording = True
        
        # 调用应用的按下处理
        if self.app and hasattr(self.app, 'handle_press'):
            await self.app.handle_press()
            
        # 触发回调
        if self.on_recording_start:
            await self._call_callback(self.on_recording_start)
            
        return True
    
    # 停止录音  
    # 对应CLI中的'e'键
    async def stop_recording(self):
        if not self.is_recording:
            return False
            
        self.is_recording = False
        
        # 调用应用的释放处理
        if self.app and hasattr(self.app, 'handle_release'):
            await self.app.handle_release()
            
        # 触发回调
        if self.on_recording_stop:
            await self._call_callback(self.on_recording_stop)
            
        return True
    
    # 获取录音状态
    def get_recording_status(self):
        device_state = "unknown"
        connected = False
        
        if self.app:
            # 获取设备状态 - device_state 本身就是字符串
            device_state = self.app.device_state if self.app.device_state else "unknown"
            
            # 获取连接状态
            if self.app.protocol:
                connected = getattr(self.app.protocol, 'connected', False)
        
        return {
            "is_recording": self.is_recording,
            "device_state": device_state,
            "connected": connected
        }
    
    # 接收文本消息
    async def on_text_message(self, text: str):
        if self.on_text_received:
            await self._call_callback(self.on_text_received, text)
    
    # 状态更新
    async def on_status_update(self, status: str, connected: bool):
        if self.on_status_changed:
            await self._call_callback(self.on_status_changed, status, connected)
    
    # 调用回调函数
    async def _call_callback(self, callback, *args):
        if asyncio.iscoroutinefunction(callback):
            await callback(*args)
        else:
            callback(*args)