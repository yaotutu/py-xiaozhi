# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

py-xiaozhi 是一个基于 Python 的 AI 语音助手客户端，支持语音交互、MCP工具系统、IoT设备控制等功能。项目采用异步架构，支持 GUI 和 CLI 双模式运行。

## 常用开发命令

### 运行应用
```bash
# GUI模式（默认）
python main.py

# CLI模式
python main.py --mode cli

# 使用MQTT协议
python main.py --protocol mqtt

# 跳过激活（调试用）
python main.py --skip-activation
```

### 代码格式化
```bash
# 运行代码格式化脚本
./format_code.sh

# 脚本会依次执行：
# 1. autoflake - 删除未使用的导入和变量
# 2. docformatter - 格式化文档字符串
# 3. isort - 排序导入语句
# 4. black - 格式化代码
# 5. flake8 - 静态代码检查
```

### 依赖管理
```bash
# 安装依赖
pip install -r requirements.txt

# 每次更新代码后重新安装依赖（防止新增依赖缺失）
pip install -r requirements.txt --upgrade
```

## 核心架构

### 应用启动流程
1. `main.py` - 入口文件，处理命令行参数，创建事件循环
2. `SystemInitializer` - 系统初始化，处理设备激活
3. `Application` - 核心应用逻辑，管理各个组件的生命周期

### 核心组件关系
- **Application** (`src/application.py`) - 应用主控制器，协调各组件
- **Protocol** (`src/protocols/`) - 通信协议层，支持WebSocket和MQTT
- **AudioCodec** (`src/audio_codecs/`) - 音频处理，包括Opus编解码、AEC回声消除
- **MCPServer** (`src/mcp/mcp_server.py`) - MCP工具服务器，管理各种工具
- **ThingManager** (`src/iot/thing_manager.py`) - IoT设备管理器
- **Display** (`src/display/`) - 显示层，支持GUI和CLI

### 异步架构要点
- 所有核心组件都基于 asyncio 实现异步操作
- 使用单例模式管理全局资源（ConfigManager、ThingManager等）
- 音频处理采用队列和流式传输，延迟控制在5ms以内
- WebSocket/MQTT通信支持自动重连和错误恢复

## 配置系统

配置文件位于 `config/config.json`，支持分层配置和点记法访问：
- `SYSTEM_OPTIONS` - 系统配置（设备ID、网络URL等）
- `WAKE_WORD_OPTIONS` - 唤醒词配置
- `CAMERA` - 摄像头配置
- `SHORTCUTS` - 快捷键配置
- `AEC_OPTIONS` - 回声消除配置

## MCP工具开发

新增MCP工具步骤：
1. 在 `src/mcp/tools/` 创建工具目录
2. 实现 `manager.py`（业务逻辑）和 `tools.py`（MCP接口）
3. 在 `mcp_server.py` 注册工具

## IoT设备开发

新增IoT设备步骤：
1. 在 `src/iot/things/` 创建设备类
2. 继承 `Thing` 基类，实现属性和方法
3. 在 `thing_manager.py` 注册设备

## 音频处理架构

- **音频输入流程**: 麦克风 → VAD检测 → Opus编码 → WebSocket发送
- **音频输出流程**: WebSocket接收 → Opus解码 → 重采样 → 扬声器播放
- **唤醒词检测**: 基于Sherpa-ONNX离线模型
- **回声消除**: 集成WebRTC AEC模块（可选开启）

## 重要文件路径

- 配置文件: `config/config.json`
- 日志文件: `logs/`
- 缓存文件: `cache/`
- 语音模型: `models/`（唤醒词模型，需单独下载）
- 音乐缓存: `cache/music/`