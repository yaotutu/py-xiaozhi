#!/usr/bin/env python3
# gRPC 调试测试脚本

import grpc
import asyncio
import traceback
from src.grpc import voice_service_pb2
from src.grpc import voice_service_pb2_grpc


async def test_grpc_service():
    # 连接到 gRPC 服务器
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = voice_service_pb2_grpc.VoiceServiceStub(channel)
    
    try:
        print("测试 gRPC 服务（调试模式）...")
        
        # 测试获取状态
        print("\n1. 测试 GetStatus RPC:")
        try:
            status = await stub.GetStatus(voice_service_pb2.Empty())
            print(f"   成功!")
            print(f"   录音中: {status.is_recording}")
            print(f"   设备状态: {status.device_state}")
            print(f"   已连接: {status.connected}")
        except grpc.RpcError as e:
            print(f"   RPC 错误: {e.code()}")
            print(f"   详情: {e.details()}")
            # 获取更详细的错误信息
            for key, value in e.trailing_metadata():
                print(f"   元数据 {key}: {value}")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"客户端错误: {e}")
        traceback.print_exc()
    finally:
        await channel.close()


# 直接测试服务层
def test_voice_service_directly():
    print("\n直接测试 VoiceService 类:")
    try:
        from src.services.voice_service import VoiceService
        
        # 创建服务实例
        service = VoiceService()
        
        # 测试获取状态（不设置app）
        status = service.get_recording_status()
        print(f"状态（无app）: {status}")
        
        # 模拟设置app
        class MockApp:
            device_state = "idle"
            protocol = None
        
        service.app = MockApp()
        status = service.get_recording_status()
        print(f"状态（有app）: {status}")
        
        print("直接测试成功!")
        
    except Exception as e:
        print(f"直接测试失败: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # 先直接测试服务
    test_voice_service_directly()
    
    # 再测试 gRPC
    print("\n" + "="*50)
    asyncio.run(test_grpc_service())