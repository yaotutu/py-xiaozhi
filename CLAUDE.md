# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

py-xiaozhi 是一个专为 Linux ARM 设备（如 Orange Pi）设计的 AI 语音助手客户端，采用纯 CLI 模式运行。支持语音交互、MCP工具系统、IoT设备控制等功能。项目基于异步架构，已精简移除所有 GUI 和跨平台代码。

## 项目特点

- **纯 Linux CLI 应用**：专为 Linux ARM 系统优化（主要在 Orange Pi 上运行），无 GUI 依赖
- **精简架构**：移除所有 Windows/macOS 代码，代码量减少约30%
- **轻量运行**：无 PyQt5/qasync 依赖，启动快速，内存占用小
- **核心功能完整**：保留所有 AI 交互、MCP工具、IoT 控制功能
- **实时音频处理**：集成 VAD、Opus 编解码、WebRTC AEC 回声消除

## 常用开发命令

### 运行应用
```bash
# 默认CLI模式运行
python main.py

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

# 卸载已移除的GUI依赖（如果之前安装过）
pip uninstall PyQt5 qasync -y

# 验证环境（检查依赖是否正确安装）
python verify_env.py
```

## 核心架构

### 应用启动流程
1. `main.py` - 入口文件，直接使用标准 asyncio 事件循环
2. `SystemInitializer` - 系统初始化，CLI 模式设备激活
3. `Application` - 核心应用逻辑，管理各个组件的生命周期

### 核心组件关系
- **Application** (`src/application.py`) - 应用主控制器，协调各组件
- **Protocol** (`src/protocols/`) - 通信协议层，支持WebSocket和MQTT
- **AudioCodec** (`src/audio_codecs/`) - 音频处理，包括Opus编解码、AEC回声消除
- **MCPServer** (`src/mcp/mcp_server.py`) - MCP工具服务器，管理各种工具
- **ThingManager** (`src/iot/thing_manager.py`) - IoT设备管理器
- **CliDisplay** (`src/display/cli_display.py`) - CLI显示界面

### 异步架构要点
- 所有核心组件都基于 asyncio 实现异步操作
- 使用单例模式管理全局资源（ConfigManager、ThingManager等）
- 音频处理采用队列和流式传输，延迟控制在5ms以内
- WebSocket/MQTT通信支持自动重连和错误恢复

## 配置系统

配置文件位于 `config/config.json`，支持分层配置和点记法访问：
- `SYSTEM_OPTIONS` - 系统配置（设备ID、网络URL、协议选择等）
- `WAKE_WORD_OPTIONS` - 唤醒词配置（模型路径、灵敏度）
- `CAMERA` - 摄像头配置（分辨率、帧率）
- `SHORTCUTS` - 快捷键配置（通过 pynput 在后台监听）
- `AEC_OPTIONS` - 回声消除配置（降噪级别、延迟参数）
- `AUDIO` - 音频配置（采样率、缓冲区大小）

## MCP工具系统

### 已集成的MCP工具
- **系统控制** (`system/`) - 应用管理、音量控制、系统状态监控
- **日程管理** (`calendar/`) - 日历事件、提醒服务、事件查询
- **定时任务** (`timer/`) - 倒计时器、定时执行、多任务管理
- **音乐播放** (`music/`) - 在线音乐搜索、播放控制、歌单管理
- **铁路查询** (`railway/`) - 12306票务查询、车次信息、余票监控
- **网络搜索** (`search/`) - 必应搜索、网页内容获取、信息提取
- **菜谱查询** (`recipe/`) - 菜谱搜索、分类查询、食材推荐
- **地图服务** (`amap/`) - 高德地图、路径规划、天气查询、POI搜索
- **八字命理** (`bazi/`) - 八字分析、婚姻分析、黄历查询、运势预测
- **摄像头** (`camera/`) - 图像捕获、AI视觉分析、场景识别
- **电池管理** (`battery/`) - 电池状态监控、电量预警（开发中）

### 新增MCP工具步骤
1. 在 `src/mcp/tools/` 创建工具目录
2. 实现 `manager.py`（业务逻辑）和 `tools.py`（MCP接口）
3. 在 `mcp_server.py` 注册工具

## IoT设备开发

### 已支持的设备
- **智能灯光** (`lamp.py`) - 开关控制、亮度调节
- **扬声器** (`speaker.py`) - 音量控制、静音管理
- **音乐播放器** (`music_player.py`) - 播放控制、歌单管理、进度控制
- **倒计时器** (`countdown_timer.py`) - 多任务倒计时、提醒功能
- **摄像头** (`CameraVL/`) - 视频流捕获、图像处理

### 新增IoT设备步骤
1. 在 `src/iot/things/` 创建设备类
2. 继承 `Thing` 基类，实现属性和方法
3. 在 `thing_manager.py` 注册设备

## 音频处理架构

- **音频输入流程**: 麦克风 → VAD检测 → Opus编码 → WebSocket发送
- **音频输出流程**: WebSocket接收 → Opus解码 → 重采样 → 扬声器播放
- **唤醒词检测**: 基于Sherpa-ONNX离线模型
- **回声消除**: 集成WebRTC AEC模块（可选开启）
- **Linux音频库**: 仅保留 Linux 平台的 libopus 和 webrtc_apm

## 重要文件路径

- 配置文件: `config/config.json`
- 日志文件: `logs/` (应用运行日志，按日期分割)
- 缓存文件: `cache/` (临时文件存储)
- 语音模型: `models/` (Sherpa-ONNX唤醒词模型，需单独下载)
- 音乐缓存: `cache/music/` (在线音乐缓存)
- Linux库文件: `libs/libopus/linux/`, `libs/webrtc_apm/linux/`
- 格式化脚本: `format_code.sh` (代码格式化工具链)

## 已移除的内容

为保持项目精简，以下内容已被移除：
- GUI相关: `src/views/`, `src/display/gui_display.py`, `assets/`
- 跨平台代码: Windows/macOS 的应用管理、库文件
- 文档网站: `documents/` 目录
- 构建配置: `build.json`, `pyproject.toml`
- GUI依赖: PyQt5, qasync

## 开发注意事项

1. **纯Linux环境**：所有新增代码应只考虑 Linux ARM 平台（主要是 Orange Pi）
2. **CLI优先**：界面交互都通过命令行实现，使用 rich 库美化输出
3. **保持精简**：避免添加不必要的依赖和代码
4. **异步编程**：使用 async/await，避免阻塞操作
5. **错误处理**：完善的异常捕获和日志记录
6. **代码规范**：运行 `./format_code.sh` 保持代码风格一致
7. **性能优化**：注意 ARM 设备的性能限制，避免占用过多资源

## 代码编写规范

### 注释规范
1. **Python注释**：必须使用 `#` 注释，禁止使用 `"""` 或 `'''` 的多行字符串作为注释
2. **注释详细度**：所有函数、类、复杂逻辑都需要添加详细的中文注释
3. **注释位置**：
   - 类和函数的说明注释放在定义的上一行
   - 代码块的注释放在代码块上方
   - 行内注释放在代码后面，使用两个空格分隔

### 注释示例
```python
# 音频处理管理器类
# 负责管理音频的编解码、VAD检测和回声消除
class AudioManager:
    # 初始化音频管理器
    # 参数:
    #   sample_rate: 采样率，默认16000
    #   channels: 通道数，默认1（单声道）
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate  # 音频采样率
        self.channels = channels  # 音频通道数
        
        # 初始化VAD检测器
        # 用于检测语音活动，过滤静音片段
        self.vad = VADDetector()
        
        # 初始化Opus编码器
        # 用于压缩音频数据，降低网络传输带宽
        self.encoder = OpusEncoder(sample_rate, channels)
```

### 其他编码规范
- **函数命名**：使用小写字母和下划线（snake_case）
- **类命名**：使用大驼峰命名法（PascalCase）
- **常量命名**：使用大写字母和下划线（UPPER_SNAKE_CASE）
- **私有成员**：使用单下划线前缀（_private_member）
- **导入顺序**：标准库 → 第三方库 → 本地模块