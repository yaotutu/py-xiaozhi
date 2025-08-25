# gRPC 服务器实现
# 提供语音控制的 gRPC 接口

import asyncio
import grpc
import time
from concurrent import futures
from typing import Optional

from src.grpc import voice_service_pb2
from src.grpc import voice_service_pb2_grpc
from src.services.voice_service import VoiceService
from src.utils.logging_config import get_logger


logger = get_logger(__name__)


# gRPC 服务实现类
class VoiceServiceImpl(voice_service_pb2_grpc.VoiceServiceServicer):
    
    def __init__(self, voice_service: VoiceService):
        # 语音服务实例
        self.voice_service = voice_service
        
        # 状态订阅者列表
        self.status_subscribers = []
        
        # 文本消息订阅者列表  
        self.text_subscribers = []
        
        # 设置回调
        self._setup_callbacks()
        
    # 设置回调函数
    def _setup_callbacks(self):
        # 录音开始回调
        self.voice_service.on_recording_start = self._on_recording_start
        
        # 录音停止回调
        self.voice_service.on_recording_stop = self._on_recording_stop
        
        # 文本消息回调
        self.voice_service.on_text_received = self._on_text_received
        
        # 状态变更回调
        self.voice_service.on_status_changed = self._on_status_changed
    
    # 开始录音 RPC
    async def StartRecording(self, request, context):
        logger.info("收到开始录音请求")
        
        try:
            # 调用语音服务开始录音
            success = await self.voice_service.start_recording()
            
            if success:
                return voice_service_pb2.RecordingResponse(
                    success=True,
                    message="录音已开始"
                )
            else:
                return voice_service_pb2.RecordingResponse(
                    success=False,
                    message="录音开始失败，可能已在录音中"
                )
                
        except Exception as e:
            logger.error(f"开始录音异常: {e}")
            return voice_service_pb2.RecordingResponse(
                success=False,
                message=f"错误: {str(e)}"
            )
    
    # 停止录音 RPC
    async def StopRecording(self, request, context):
        logger.info("收到停止录音请求")
        
        try:
            # 调用语音服务停止录音
            success = await self.voice_service.stop_recording()
            
            if success:
                return voice_service_pb2.RecordingResponse(
                    success=True,
                    message="录音已停止"
                )
            else:
                return voice_service_pb2.RecordingResponse(
                    success=False,
                    message="录音停止失败，当前未在录音"
                )
                
        except Exception as e:
            logger.error(f"停止录音异常: {e}")
            return voice_service_pb2.RecordingResponse(
                success=False,
                message=f"错误: {str(e)}"
            )
    
    # 获取状态 RPC
    async def GetStatus(self, request, context):
        # 获取当前状态
        status = self.voice_service.get_recording_status()
        
        return voice_service_pb2.StatusResponse(
            is_recording=status["is_recording"],
            device_state=status["device_state"],
            connected=status["connected"]
        )
    
    # 订阅状态流 RPC
    async def SubscribeStatus(self, request, context):
        logger.info("新的状态订阅者")
        
        # 创建队列接收状态更新
        queue = asyncio.Queue()
        self.status_subscribers.append(queue)
        
        try:
            # 发送初始状态
            status = self.voice_service.get_recording_status()
            yield voice_service_pb2.StatusUpdate(
                status="initial",
                connected=status["connected"],
                is_recording=status["is_recording"],
                device_state=status["device_state"],
                timestamp=int(time.time() * 1000)
            )
            
            # 持续发送状态更新
            while not context.is_active():
                try:
                    # 等待状态更新
                    update = await asyncio.wait_for(queue.get(), timeout=30)
                    yield update
                except asyncio.TimeoutError:
                    # 发送心跳
                    status = self.voice_service.get_recording_status()
                    yield voice_service_pb2.StatusUpdate(
                        status="heartbeat",
                        connected=status["connected"],
                        is_recording=status["is_recording"],
                        device_state=status["device_state"],
                        timestamp=int(time.time() * 1000)
                    )
                    
        finally:
            # 移除订阅者
            if queue in self.status_subscribers:
                self.status_subscribers.remove(queue)
            logger.info("状态订阅者断开")
    
    # 订阅文本消息流 RPC
    async def SubscribeTextMessages(self, request, context):
        logger.info("新的文本消息订阅者")
        
        # 创建队列接收文本消息
        queue = asyncio.Queue()
        self.text_subscribers.append(queue)
        
        try:
            # 持续发送文本消息
            while not context.is_active():
                try:
                    # 等待文本消息
                    message = await asyncio.wait_for(queue.get(), timeout=60)
                    yield message
                except asyncio.TimeoutError:
                    # 继续等待，不发送心跳
                    continue
                    
        finally:
            # 移除订阅者
            if queue in self.text_subscribers:
                self.text_subscribers.remove(queue)
            logger.info("文本消息订阅者断开")
    
    # 录音开始回调
    async def _on_recording_start(self):
        # 广播状态更新给所有订阅者
        status = self.voice_service.get_recording_status()
        update = voice_service_pb2.StatusUpdate(
            status="recording_started",
            connected=status["connected"],
            is_recording=True,
            device_state=status["device_state"],
            timestamp=int(time.time() * 1000)
        )
        
        for queue in self.status_subscribers:
            await queue.put(update)
    
    # 录音停止回调
    async def _on_recording_stop(self):
        # 广播状态更新给所有订阅者
        status = self.voice_service.get_recording_status()
        update = voice_service_pb2.StatusUpdate(
            status="recording_stopped",
            connected=status["connected"],
            is_recording=False,
            device_state=status["device_state"],
            timestamp=int(time.time() * 1000)
        )
        
        for queue in self.status_subscribers:
            await queue.put(update)
    
    # 文本消息回调
    async def _on_text_received(self, text: str, msg_type: str = "assistant"):
        # 广播文本消息给所有订阅者
        message = voice_service_pb2.TextMessage(
            text=text,
            type=msg_type,
            timestamp=int(time.time() * 1000)
        )
        
        for queue in self.text_subscribers:
            await queue.put(message)
    
    # 状态变更回调
    async def _on_status_changed(self, status: str, connected: bool):
        # 广播状态更新给所有订阅者
        current_status = self.voice_service.get_recording_status()
        update = voice_service_pb2.StatusUpdate(
            status=status,
            connected=connected,
            is_recording=current_status["is_recording"],
            device_state=current_status["device_state"],
            timestamp=int(time.time() * 1000)
        )
        
        for queue in self.status_subscribers:
            await queue.put(update)


# gRPC 服务器类
class GrpcServer:
    
    def __init__(self, voice_service: VoiceService, host: str = "0.0.0.0", port: int = 50051):
        # 语音服务
        self.voice_service = voice_service
        
        # 服务器地址和端口
        self.host = host
        self.port = port
        
        # gRPC 服务器实例
        self.server: Optional[grpc.aio.Server] = None
        
        # 日志
        self.logger = get_logger("grpc_server")
    
    # 启动服务器
    async def start(self):
        self.logger.info(f"启动 gRPC 服务器，地址: {self.host}:{self.port}")
        
        # 创建 gRPC 服务器
        self.server = grpc.aio.server()
        
        # 添加服务实现
        service_impl = VoiceServiceImpl(self.voice_service)
        voice_service_pb2_grpc.add_VoiceServiceServicer_to_server(
            service_impl, self.server
        )
        
        # 绑定地址和端口
        listen_addr = f"{self.host}:{self.port}"
        self.server.add_insecure_port(listen_addr)
        
        # 启动服务器
        await self.server.start()
        
        self.logger.info(f"gRPC 服务器已启动，监听地址: {listen_addr}")
    
    # 停止服务器
    async def stop(self):
        if self.server:
            self.logger.info("停止 gRPC 服务器")
            await self.server.stop(grace=5)
            self.server = None
            self.logger.info("gRPC 服务器已停止")
    
    # 等待服务器终止
    async def wait_for_termination(self):
        if self.server:
            await self.server.wait_for_termination()