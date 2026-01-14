# 第一天工作指南：机器人头表情映射探索

今天的目标是让你快速上手我们的 MLOps（机器学习运维）流程，并对核心开源仓库进行初步调研，为明天下午的周会汇报做好准备。

> [!IMPORTANT]
> **机器人硬件控制接口**：我们已经收悉了 3 电机机器人头（嘴巴、眼球、眼皮）的官方 TTL 指令集。请务必详细阅读 [ttl控制指令.md](file:///c:/work/code/face/docs/hardware/ttl%E6%8E%A7%E5%88%B6%E6%8C%87%E4%BB%A4.md) 了解完整协议。
> 
> **指令简要说明**：
> - **嘴巴 (Mouth)**：`#DGM:1!` (闭嘴) 到 `#DGM:5!` (完全张开)
> - **眼球 (Eyeball)**：`$DGB:1!` 到 `$DGB:21!` (位置参考 [眼球运动.png](file:///c:/work/code/face/docs/hardware/%E7%9C%BC%E7%90%83%E8%BF%90%E5%8A%A8.png))
> - **眼皮 (Eyelid)**：`$DGL:1!` (正常睁眼) 到 `$DGL:3!` (闭眼)

## 任务 1：演示 MLOps 流程 (MLflow + DVC + ZenML)
你需要使用一个最简化的案例来跑通整个工具链。

### 环境准备
在 PowerShell 或 CMD 中执行以下命令：
```powershell
# 1. 创建并激活虚拟环境 (Windows)
python -m venv venv
.\venv\Scripts\activate

# 2. 安装核心依赖
pip install zenml mlflow dvc scikit-learn pandas numpy

# 3. 初始化工具
zenml init
dvc init
```

### 2. 注册并设置 ZenML Stack (用于实验跟踪)
在同一终端中运行：
```powershell
# 注册 MLflow tracker 组件
zenml experiment-tracker register mlflow_tracker --flavor=mlflow

# 注册并设置完整的 Stack (环境快照)
zenml stack register local_mlflow_stack -o default -e mlflow_tracker
zenml stack set local_mlflow_stack
```

### 运行 Demo
1. 查看并运行我们提供的 [demo_mlops.py](file:///c:/work/code/face/pipelines/demo_mlops.py)。
2. 运行完成后，查看 MLflow UI：
   ```bash
   mlflow ui
   ```
   在浏览器中访问 `http://localhost:5000`，确认看到了 `mse` 指标和 `model_type` 参数。
3. **DVC 部分建议**：尝试对 `data.csv` 进行一次修改，运行 `dvc add data.csv` 并观察 `data.csv.dvc` 文件的变化。

---

## 任务 2：核心仓库调研与 Demo 推进
你需要深入研究以下两个仓库，并回答：**“我们首先要从哪里下手，向『快速实现 demo 和测试』的目标推进？”**

### 1. [Voice_Driven_Humanoid_Head](https://github.com/acromtech/Voice_Driven_Humanoid_Head)
- **核心能力**：该仓库实现了一个完整的语音交互闭环（Whisper 语音转文字 -> GPT 处理/TTS 语音合成 -> 舵机控制）。
- **我们的切入点**：
    - 它的硬件接口与我们的 3 电机系统非常相似（都是串口控制）。
    - **重点：** 寻找它的 `serial` 通讯部分，尝试将其舵机指令替换为我们的指令格式（如 `#DGM:1!`）。
    - 验证：能否通过它现成的语音循环，触发我们的机器人头动作？

### 2. [OpenRoboExp](https://github.com/library87/OpenRoboExp)
- **核心能力**：专注于“表情”的精细化合成。它支持将 ARKit 的 52 个 blendshapes 映射到机器人硬件。
- **我们的切入点**：
    - 我们的机器人只有 3 个部分（嘴、眼球、眼皮），我们需要从中提取最关键的参数（如 `jawOpen`, `eyeBlink`, `lookAt`）。
    - **重点：** 研究它的映射函数，看看它是如何处理数值到离散指令（#DGM等）转换的。

### 3. 如何进行“无硬件模拟” (Mocking)
既然目前你手里没有硬件，请通过以下方式修改代码来实现“虚拟测试”：

在代码中寻找负责 `serial.write`（串口写入）的部分。在 Windows 上，串口号通常是 `COM3`, `COM4` 等。你可以将其逻辑修改为如下方式观察输出：

```python
# --- 模拟初始化 ---
# 原始代码: ser = Serial('COM3', 9600)
# 修改后的 Mock 逻辑:
print("[SERIAL MOCK] 正在模拟打开串口 COM3...")

# --- 模拟发送指令 ---
# 原始代码: ser.write(f'#DGM:{val}!'.encode())
# 修改后的 Mock 逻辑:
print(f"[SERIAL MOCK] 硬件执行指令中: #DGM:{val}!")
```

### 下步行动建议 (用于明天下午开会汇报)
- **汇报建议**：演示上述 [demo_mlops.py](file:///c:/work/code/face/pipelines/demo_mlops.py) 的运行结果。
- **技术路线建议**：
    1. **第一阶段 (Demo 优先)**：以 `Voice_Driven_Humanoid_Head` 为骨架，复用其语音交互流程。
    2. **第二阶段 (精细化控制)**：引入 `PantoMatrix` 或 `OpenRoboExp` 的预训练模型，将语音特征映射为更有表现力的指令。
    3. **第三阶段 (训练增强)**：使用 sEMG 传感器数据，通过我们搭建的 MLOps 平台训练专属的映射模型。

---

## 参考文档
- [调研报告 (research.md)](file:///c:/work/code/face/docs/research/research.md)
- [MLOps 方案 (mlops.md)](file:///c:/work/code/face/docs/mlops.md)
- [DVC 与 dvc.yaml 指引 (dvc_guide.md)](file:///c:/work/code/face/docs/guides/dvc_guide.md)
- [项目架构指引 (project_architecture.md)](file:///c:/work/code/face/docs/project_architecture.md)
