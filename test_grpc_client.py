#!/usr/bin/env python3
# gRPC 客户端测试脚本

import grpc
import asyncio
import sys
from src.grpc import voice_service_pb2
from src.grpc import voice_service_pb2_grpc


async def test_grpc_service():
    # 连接到 gRPC 服务器
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = voice_service_pb2_grpc.VoiceServiceStub(channel)
    
    try:
        print("测试 gRPC 服务...")
        
        # 测试获取状态
        print("\n1. 获取状态:")
        status = await stub.GetStatus(voice_service_pb2.Empty())
        print(f"   录音中: {status.is_recording}")
        print(f"   设备状态: {status.device_state}")
        print(f"   已连接: {status.connected}")
        
        # 测试开始录音
        print("\n2. 开始录音:")
        response = await stub.StartRecording(voice_service_pb2.Empty())
        print(f"   成功: {response.success}")
        print(f"   消息: {response.message}")
        
        # 等待一秒
        await asyncio.sleep(1)
        
        # 再次获取状态
        print("\n3. 再次获取状态:")
        status = await stub.GetStatus(voice_service_pb2.Empty())
        print(f"   录音中: {status.is_recording}")
        
        # 测试停止录音
        print("\n4. 停止录音:")
        response = await stub.StopRecording(voice_service_pb2.Empty())
        print(f"   成功: {response.success}")
        print(f"   消息: {response.message}")
        
        print("\n测试完成!")
        
    except grpc.RpcError as e:
        print(f"gRPC 错误: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        await channel.close()


if __name__ == "__main__":
    asyncio.run(test_grpc_service())