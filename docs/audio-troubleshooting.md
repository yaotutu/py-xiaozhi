# 音频故障排查指南

本文档帮助您解决 py-xiaozhi 应用中的音频输入/输出问题。

## 快速诊断

### 检查音频服务状态
```bash
# 检查 PulseAudio 是否运行
systemctl --user status pulseaudio

# 查看 PulseAudio 服务信息
pactl info
```

## 一、音频输出故障排查（没有声音）

### 1. 查看当前默认输出设备
```bash
# 查看默认输出设备
pactl info | grep "Default Sink"

# 列出所有可用的输出设备
pactl list short sinks

# 查看输出设备详细信息
pactl list sinks
```

### 2. 检查音量和静音状态
```bash
# 查看默认输出设备的音量
pactl list sinks | grep -A 10 "$(pactl info | grep 'Default Sink' | cut -d: -f2)"

# 检查是否静音
pactl list sinks | grep Mute

# 解除静音
pactl set-sink-mute @DEFAULT_SINK@ 0

# 设置音量（70%）
pactl set-sink-volume @DEFAULT_SINK@ 70%
```

### 3. 切换输出设备
```bash
# 列出所有输出设备
pactl list short sinks
# 输出示例：
# 0    alsa_output.platform-hdmi-sound.stereo-fallback    module-alsa-card.c    s16le 2ch 44100Hz    SUSPENDED
# 1    alsa_output.platform-heaadphones-sound.stereo-fallback    module-alsa-card.c    s16le 2ch 44100Hz    RUNNING

# 切换到耳机输出
pactl set-default-sink alsa_output.platform-heaadphones-sound.stereo-fallback

# 切换到HDMI输出
pactl set-default-sink alsa_output.platform-hdmi-sound.stereo-fallback

# 或使用索引号切换
pactl set-default-sink 1
```

### 4. 测试音频输出
```bash
# 播放测试音
speaker-test -t sine -f 440 -l 1

# 使用 paplay 播放测试音
paplay /usr/share/sounds/alsa/Front_Center.wav

# 查看正在播放的音频流
pactl list short sink-inputs
```

## 二、音频输入故障排查（无法录音）

### 1. 查看当前默认输入设备
```bash
# 查看默认输入设备
pactl info | grep "Default Source"

# 列出所有可用的输入设备
pactl list short sources

# 查看输入设备详细信息
pactl list sources
```

### 2. 检查麦克风音量和静音状态
```bash
# 查看默认输入设备的音量
pactl list sources | grep -A 10 "$(pactl info | grep 'Default Source' | cut -d: -f2)"

# 解除麦克风静音
pactl set-source-mute @DEFAULT_SOURCE@ 0

# 设置麦克风音量（80%）
pactl set-source-volume @DEFAULT_SOURCE@ 80%
```

### 3. 切换输入设备
```bash
# 列出所有输入设备
pactl list short sources
# 输出示例：
# 0    alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono    module-alsa-card.c    s16le 1ch 44100Hz    RUNNING
# 1    alsa_input.platform-es8316-sound.analog-stereo    module-alsa-card.c    s16le 2ch 44100Hz    SUSPENDED

# 切换到USB麦克风
pactl set-default-source alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono

# 或使用索引号切换
pactl set-default-source 0
```

### 4. 测试麦克风
```bash
# 录音5秒测试
arecord -d 5 test.wav

# 播放录音
aplay test.wav

# 实时监听麦克风输入（按Ctrl+C停止）
pacat -r | pacat -p

# 查看麦克风输入电平
pavucontrol  # 图形界面工具（如果可用）
```

## 三、常见问题和解决方案

### 问题1：应用启动后没有声音

**可能原因**：默认输出设备设置错误

**解决方案**：
```bash
# 1. 确认耳机/扬声器已连接
# 2. 查看当前默认输出
pactl info | grep "Default Sink"

# 3. 如果是HDMI输出，切换到耳机
pactl set-default-sink alsa_output.platform-heaadphones-sound.stereo-fallback

# 4. 测试声音
speaker-test -t sine -f 440 -l 1
```

### 问题2：麦克风无法录音

**可能原因**：默认输入设备错误或被静音

**解决方案**：
```bash
# 1. 列出所有输入设备
pactl list short sources

# 2. 设置正确的输入设备
pactl set-default-source alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono

# 3. 解除静音并设置音量
pactl set-source-mute @DEFAULT_SOURCE@ 0
pactl set-source-volume @DEFAULT_SOURCE@ 80%
```

### 问题3：音量太小

**解决方案**：
```bash
# 提高输出音量到100%
pactl set-sink-volume @DEFAULT_SINK@ 100%

# 提高麦克风音量到100%
pactl set-source-volume @DEFAULT_SOURCE@ 100%

# 也可以使用百分比增量
pactl set-sink-volume @DEFAULT_SINK@ +10%  # 增加10%
```

### 问题4：有回声或噪音

**解决方案**：
```bash
# 加载回声消除模块
pactl load-module module-echo-cancel

# 查看已加载的模块
pactl list short modules

# 卸载模块（使用模块ID）
pactl unload-module <module_id>
```

## 四、高级调试

### 1. 实时监控音频系统
```bash
# 监控 PulseAudio 日志
journalctl -u pulseaudio -f

# 查看详细的设备信息
pactl list cards

# 查看音频流信息
pactl list sink-inputs  # 输出流
pactl list source-outputs  # 输入流
```

### 2. 重启音频服务
```bash
# 重启 PulseAudio
systemctl --user restart pulseaudio

# 或者
pulseaudio -k  # 杀死当前进程
pulseaudio --start  # 重新启动
```

### 3. 检查 ALSA 底层
```bash
# 查看 ALSA 声卡
cat /proc/asound/cards

# 查看 ALSA 设备
aplay -l  # 播放设备
arecord -l  # 录音设备

# 使用 ALSA 混音器调整音量
alsamixer
```

## 五、保存和恢复音频配置

### 保存当前工作的配置
```bash
# 保存当前音频配置
pactl info > ~/.config/py-xiaozhi/working_audio_config.txt
pactl list short sinks >> ~/.config/py-xiaozhi/working_audio_config.txt
pactl list short sources >> ~/.config/py-xiaozhi/working_audio_config.txt
```

### 创建音频恢复脚本
```bash
# 创建恢复脚本
cat > ~/restore_audio.sh << 'EOF'
#!/bin/bash
# 恢复音频到正常工作状态

# 设置默认输出为耳机
pactl set-default-sink alsa_output.platform-heaadphones-sound.stereo-fallback

# 设置默认输入为USB麦克风
pactl set-default-source alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono

# 解除静音
pactl set-sink-mute @DEFAULT_SINK@ 0
pactl set-source-mute @DEFAULT_SOURCE@ 0

# 设置合理的音量
pactl set-sink-volume @DEFAULT_SINK@ 70%
pactl set-source-volume @DEFAULT_SOURCE@ 80%

echo "音频配置已恢复"
pactl info | grep -E "Default Sink|Default Source"
EOF

chmod +x ~/restore_audio.sh
```

## 六、应用相关提示

### py-xiaozhi 音频系统说明

1. **音频链路**：
   ```
   应用 → sounddevice → PortAudio → PulseAudio → ALSA → 硬件
   ```

2. **关键配置**：
   - 输入采样率：16kHz（录音和识别）
   - 输出采样率：24kHz（播放）
   - 音频格式：16位 PCM
   - 通道数：单声道

3. **验证应用音频状态**：
   ```bash
   # 应用运行时，查看音频流
   pactl list short sink-inputs | grep python
   pactl list short source-outputs | grep python
   ```

## 七、快速修复命令集

```bash
# 一键恢复默认音频（适用于 Orange Pi）
pactl set-default-sink alsa_output.platform-heaadphones-sound.stereo-fallback && \
pactl set-default-source alsa_input.usb-C-Media_Electronics_Inc._USB_PnP_Sound_Device-00.analog-mono && \
pactl set-sink-mute @DEFAULT_SINK@ 0 && \
pactl set-source-mute @DEFAULT_SOURCE@ 0 && \
pactl set-sink-volume @DEFAULT_SINK@ 70% && \
pactl set-source-volume @DEFAULT_SOURCE@ 80% && \
echo "音频已恢复" && \
pactl info | grep -E "Default Sink|Default Source"
```

## 需要帮助？

如果以上方法都无法解决问题，请收集以下信息：

```bash
# 生成诊断报告
echo "=== 音频诊断报告 ===" > audio_diagnostic.txt
date >> audio_diagnostic.txt
echo -e "\n--- PulseAudio 信息 ---" >> audio_diagnostic.txt
pactl info >> audio_diagnostic.txt
echo -e "\n--- 输出设备 ---" >> audio_diagnostic.txt
pactl list short sinks >> audio_diagnostic.txt
echo -e "\n--- 输入设备 ---" >> audio_diagnostic.txt
pactl list short sources >> audio_diagnostic.txt
echo -e "\n--- ALSA 设备 ---" >> audio_diagnostic.txt
aplay -l >> audio_diagnostic.txt
arecord -l >> audio_diagnostic.txt
echo -e "\n--- 系统信息 ---" >> audio_diagnostic.txt
uname -a >> audio_diagnostic.txt
echo "报告已生成: audio_diagnostic.txt"
```

将 `audio_diagnostic.txt` 文件内容提供给技术支持。