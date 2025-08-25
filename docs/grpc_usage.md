# gRPC 服务使用指南

## 概述

py-xiaozhi 提供了 gRPC 服务接口，允许其他应用程序远程控制语音助手的录音功能、查询状态以及接收实时消息。

## 服务配置

在 `config/config.json` 中配置 gRPC 服务：

```json
{
  "GRPC": {
    "ENABLED": true,        // 是否启用 gRPC 服务
    "PORT": 50051,          // 服务端口
    "HOST": "0.0.0.0",      // 监听地址（0.0.0.0 表示所有网络接口）
    "MAX_WORKERS": 10       // 最大工作线程数
  }
}
```

## 服务接口定义

### Proto 文件

服务定义位于 `protos/voice_service.proto`：

```protobuf
service VoiceService {
  // 开始录音
  rpc StartRecording(Empty) returns (RecordingResponse);
  
  // 停止录音
  rpc StopRecording(Empty) returns (RecordingResponse);
  
  // 获取状态
  rpc GetStatus(Empty) returns (StatusResponse);
  
  // 订阅状态流（服务端推送）
  rpc SubscribeStatus(Empty) returns (stream StatusUpdate);
  
  // 订阅文本消息流（服务端推送）
  rpc SubscribeTextMessages(Empty) returns (stream TextMessage);
}
```

### 消息类型

- **RecordingResponse**: 录音操作响应
  - `success` (bool): 操作是否成功
  - `message` (string): 响应消息

- **StatusResponse**: 状态信息
  - `is_recording` (bool): 是否正在录音
  - `device_state` (string): 设备状态（idle/connecting/listening/speaking）
  - `connected` (bool): 是否已连接到服务器

- **StatusUpdate**: 状态更新（流式）
  - `status` (string): 状态描述
  - `connected` (bool): 连接状态
  - `is_recording` (bool): 录音状态
  - `device_state` (string): 设备状态
  - `timestamp` (int64): 时间戳（毫秒）

- **TextMessage**: 文本消息（流式）
  - `text` (string): 消息内容
  - `type` (string): 消息类型（user/assistant/system）
  - `timestamp` (int64): 时间戳（毫秒）

## 客户端示例

### Python 客户端

```python
import grpc
import asyncio
from src.grpc import voice_service_pb2
from src.grpc import voice_service_pb2_grpc

async def control_recording():
    # 连接到 gRPC 服务器
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = voice_service_pb2_grpc.VoiceServiceStub(channel)
    
    try:
        # 获取当前状态
        status = await stub.GetStatus(voice_service_pb2.Empty())
        print(f"设备状态: {status.device_state}")
        print(f"录音状态: {status.is_recording}")
        print(f"连接状态: {status.connected}")
        
        # 开始录音
        response = await stub.StartRecording(voice_service_pb2.Empty())
        if response.success:
            print("录音已开始")
        
        # 等待3秒
        await asyncio.sleep(3)
        
        # 停止录音
        response = await stub.StopRecording(voice_service_pb2.Empty())
        if response.success:
            print("录音已停止")
            
    finally:
        await channel.close()

# 运行示例
asyncio.run(control_recording())
```

### 订阅状态更新

```python
async def subscribe_status():
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = voice_service_pb2_grpc.VoiceServiceStub(channel)
    
    try:
        # 订阅状态流
        async for update in stub.SubscribeStatus(voice_service_pb2.Empty()):
            print(f"[{update.timestamp}] 状态: {update.status}")
            print(f"  录音: {update.is_recording}, 连接: {update.connected}")
            print(f"  设备状态: {update.device_state}")
            
    except grpc.RpcError as e:
        print(f"错误: {e}")
    finally:
        await channel.close()

asyncio.run(subscribe_status())
```

### Node.js 客户端

首先安装依赖：
```bash
npm install @grpc/grpc-js @grpc/proto-loader
```

客户端代码：
```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// 加载 proto 文件
const PROTO_PATH = path.join(__dirname, 'protos/voice_service.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});

const voice = grpc.loadPackageDefinition(packageDefinition).voice;

// 创建客户端
const client = new voice.VoiceService(
    'localhost:50051',
    grpc.credentials.createInsecure()
);

// 获取状态
client.GetStatus({}, (err, response) => {
    if (err) {
        console.error('错误:', err);
        return;
    }
    console.log('状态:', response);
});

// 开始录音
client.StartRecording({}, (err, response) => {
    if (err) {
        console.error('错误:', err);
        return;
    }
    console.log('开始录音:', response.message);
});

// 订阅状态流
const call = client.SubscribeStatus({});
call.on('data', (update) => {
    console.log('状态更新:', update);
});
call.on('error', (err) => {
    console.error('流错误:', err);
});
```

### Go 客户端

首先生成 Go 代码：
```bash
protoc --go_out=. --go-grpc_out=. protos/voice_service.proto
```

客户端代码：
```go
package main

import (
    "context"
    "log"
    "time"
    
    "google.golang.org/grpc"
    pb "your-module/voice" // 替换为你的模块路径
)

func main() {
    // 连接到 gRPC 服务器
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("连接失败: %v", err)
    }
    defer conn.Close()
    
    client := pb.NewVoiceServiceClient(conn)
    ctx := context.Background()
    
    // 获取状态
    status, err := client.GetStatus(ctx, &pb.Empty{})
    if err != nil {
        log.Fatalf("获取状态失败: %v", err)
    }
    log.Printf("状态: 录音=%v, 设备=%s, 连接=%v", 
        status.IsRecording, status.DeviceState, status.Connected)
    
    // 开始录音
    resp, err := client.StartRecording(ctx, &pb.Empty{})
    if err != nil {
        log.Fatalf("开始录音失败: %v", err)
    }
    log.Printf("开始录音: %s", resp.Message)
    
    // 等待3秒
    time.Sleep(3 * time.Second)
    
    // 停止录音
    resp, err = client.StopRecording(ctx, &pb.Empty{})
    if err != nil {
        log.Fatalf("停止录音失败: %v", err)
    }
    log.Printf("停止录音: %s", resp.Message)
}
```

### C# 客户端

使用 NuGet 安装依赖：
```bash
dotnet add package Grpc.Net.Client
dotnet add package Google.Protobuf
dotnet add package Grpc.Tools
```

客户端代码：
```csharp
using System;
using System.Threading.Tasks;
using Grpc.Core;
using Grpc.Net.Client;
using Voice; // 生成的命名空间

class Program
{
    static async Task Main(string[] args)
    {
        // 创建 gRPC 通道
        using var channel = GrpcChannel.ForAddress("http://localhost:50051");
        var client = new VoiceService.VoiceServiceClient(channel);
        
        // 获取状态
        var status = await client.GetStatusAsync(new Empty());
        Console.WriteLine($"状态: 录音={status.IsRecording}, " +
                         $"设备={status.DeviceState}, " +
                         $"连接={status.Connected}");
        
        // 开始录音
        var response = await client.StartRecordingAsync(new Empty());
        Console.WriteLine($"开始录音: {response.Message}");
        
        // 等待3秒
        await Task.Delay(3000);
        
        // 停止录音
        response = await client.StopRecordingAsync(new Empty());
        Console.WriteLine($"停止录音: {response.Message}");
        
        // 订阅状态流
        using var call = client.SubscribeStatus(new Empty());
        await foreach (var update in call.ResponseStream.ReadAllAsync())
        {
            Console.WriteLine($"[{update.Timestamp}] 状态更新: {update.Status}");
        }
    }
}
```

## 使用 grpcurl 测试

[grpcurl](https://github.com/fullstorydev/grpcurl) 是一个命令行工具，用于测试 gRPC 服务。

### 安装 grpcurl

```bash
# Linux ARM64
wget https://github.com/fullstorydev/grpcurl/releases/download/v1.8.9/grpcurl_1.8.9_linux_arm64.tar.gz
tar -xzf grpcurl_1.8.9_linux_arm64.tar.gz

# macOS
brew install grpcurl

# Windows
# 从 GitHub releases 下载对应版本
```

### 测试命令

```bash
# 列出服务
grpcurl -plaintext -proto protos/voice_service.proto localhost:50051 list

# 获取状态
grpcurl -plaintext -proto protos/voice_service.proto \
    localhost:50051 voice.VoiceService/GetStatus

# 开始录音
grpcurl -plaintext -proto protos/voice_service.proto \
    localhost:50051 voice.VoiceService/StartRecording

# 停止录音
grpcurl -plaintext -proto protos/voice_service.proto \
    localhost:50051 voice.VoiceService/StopRecording

# 订阅状态流
grpcurl -plaintext -proto protos/voice_service.proto \
    localhost:50051 voice.VoiceService/SubscribeStatus

# 订阅文本消息流
grpcurl -plaintext -proto protos/voice_service.proto \
    localhost:50051 voice.VoiceService/SubscribeTextMessages
```

## 安全注意事项

1. **网络安全**
   - 当前实现使用不安全的连接（insecure）
   - 生产环境建议使用 TLS/SSL 加密
   - 可以添加认证机制（如 JWT token）

2. **访问控制**
   - 默认监听 0.0.0.0 允许所有网络访问
   - 建议在防火墙中限制访问端口
   - 可以设置 HOST 为 127.0.0.1 仅允许本地访问

3. **并发限制**
   - MAX_WORKERS 配置限制最大并发连接数
   - 避免资源耗尽攻击

## 故障排查

### 连接失败

1. 检查服务是否启动：
   ```bash
   # 查看日志中是否有 "gRPC 服务已启动" 消息
   grep "gRPC" logs/*.log
   ```

2. 检查端口是否被占用：
   ```bash
   netstat -tlnp | grep 50051
   ```

3. 检查防火墙设置：
   ```bash
   sudo ufw status
   ```

### 代理问题

如果遇到代理相关错误，清除代理环境变量：
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

### 调试模式

启用 gRPC 调试日志：
```python
import os
os.environ['GRPC_VERBOSITY'] = 'DEBUG'
os.environ['GRPC_TRACE'] = 'all'
```

## 扩展开发

如需添加新的 RPC 方法：

1. 修改 `protos/voice_service.proto` 添加新接口
2. 重新生成代码：
   ```bash
   python -m grpc_tools.protoc -I./protos \
       --python_out=./src/grpc \
       --grpc_python_out=./src/grpc \
       ./protos/voice_service.proto
   ```
3. 在 `src/grpc/grpc_server.py` 中实现新方法
4. 更新 `src/services/voice_service.py` 添加业务逻辑

## 相关文件

- Proto 定义：`protos/voice_service.proto`
- 服务实现：`src/grpc/grpc_server.py`
- 业务逻辑：`src/services/voice_service.py`
- 测试脚本：`test_grpc_client.py`
- 配置文件：`config/config.json`