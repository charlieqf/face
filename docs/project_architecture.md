# 机器人头表情映射项目：推荐目录架构 (V1.0)

基于 MLOps (ZenML + DVC) 和 硬件解耦的构想，建议采用以下目录结构。此结构旨在支持从“纯软件模拟”平滑过渡到“真实硬件部署”。

```text
robo-head-expression/
├── .zen/                    # ZenML 内部配置（自动生成）
├── .dvc/                    # DVC 内部配置（自动生成）
├── data/                    # 数据目录 (由 DVC 管理)
│   ├── raw/                 # 原始采集数据 (sEMG .csv, 语音 .wav)
│   ├── processed/           # 特征提取后的数据 (特征矩阵)
│   └── external/            # 第三方数据集 (如 VOCA, ARKit 样本)
├── models/                  # 模型产物
│   ├── registry/            # 训练导出的 ONNX 模型
│   └── scalers/             # 预处理用的缩放器 (StandardScaler 等)
├── pipelines/               # ZenML 管道定义
│   ├── training_pipeline.py # 完整训练流程
│   ├── data_collection.py   # 数据采集与自动化标注管道
│   └── deployment_step.py   # 模型部署与 ONNX 转换逻辑
├── src/                     # 核心源代码
│   ├── brain/               # AI 逻辑层
│   │   ├── models.py        # 模型架构定义 (PyTorch/TF)
│   │   ├── mapping.py       # 数值到 TTL 指令的映射算法
│   │   └── inference.py     # 实时推理引擎 (ONNX Runtime)
│   ├── sensors/             # 传感器接入层
│   │   ├── semg_reader.py   # sEMG 传感器数据读取
│   │   └── audio_processor.py# 语音特征提取 (Wav2Vec2/RMS)
│   ├── hardware/            # 硬件驱动层
│   │   ├── serial_port.py   # 串口通讯封装 (支持 Mock 模式)
│   │   └── ttl_formatter.py # TTL 指令拼装 (#DGM, $DGB, $DGL)
│   └── utils/               # 工具类 (日志、配置解析)
├── scripts/                 # 运维与单点脚本
│   ├── collect_data.py      # 手动数据采集工具
│   ├── test_hardware.py     # 硬件指令压力测试
│   └── setup_env.sh         # 环境一键配置脚本
├── docs/                    # 项目文档
│   ├── research/            # 调研报告 (research.md)
│   ├── hardware/            # 指令集与原理图 (ttl控制指令.md)
│   └── guides/              # 员工手册 (work_guide_day1.md)
├── requirements.txt         # 项目依赖
├── dvc.yaml                 # DVC 管道定义
├── config.yaml              # 全局参数配置 (串口号、超参数等)
└── main.py                  # 项目总入口 (启动实时交互或训练)
```

## 设计核心思想：

### 1. 关注点分离 (SoC)
- **`src/hardware/`** 只负责发指令，不关心指令怎么来的。
- **`src/brain/`** 只负责算等级，不关心动作怎么执行。
- 这样员工即使没有硬件，只需在 `serial_port.py` 里开启 `MOCK_MODE`，整个 Brain 层的逻辑依然可以完整运行。

### 2. MLOps 深度集成
- **数据与逻辑分离**：`data/` 下的大文件永不进入 Git，通过 `dvc.yaml` 确保数据预处理过程是可追溯、可复现的。
- **Pipeline 化**：所有的训练不再是散落的脚本，而是统一放在 `pipelines/` 下，通过 ZenML 进行编排，确保每个模型都有“出生证明”。

### 3. 可扩展性
- 未来如果引入 `Voice_Driven_Humanoid_Head` 的语音逻辑，可以平滑地集成在 `src/sensors/audio_processor.py` 中。
- 如果引入 `OpenRoboExp` 的复杂映射，只需更新 `src/brain/mapping.py`。

---

## 开发者快速指引 (新员工必读)

为了让你更顺快地参与项目，请遵循以下开发约定：

### 1. 我该在哪里添加代码？

| 开发需求 | 目标路径 | 说明 |
| :--- | :--- | :--- |
| **新增传感器信号** | `src/sensors/` | 如新的 sEMG 预处理逻辑、实时音频流捕获等。 |
| **优化映射算法** | `src/brain/` | 调整数值到表情等级的转换逻辑，或增加新的机器学习模型。 |
| **适配新硬件指令** | `src/hardware/` | 如果机器人增加了新关节或修改了串口协议。 |
| **新建训练流水线** | `pipelines/` | 定义新的 ZenML Pipeline (加载 -> 训练 -> 评估)。 |
| **编写工具脚本** | `scripts/` | 编写一次性的数据标注工具或硬件调试批处理脚本。 |

### 2. 我该在哪里查看产出？

*   **原始与特征数据**：查看 `data/raw/` 和 `data/processed/`。注意：大文件受 DVC 保护，需使用 `dvc pull` 同步。
*   **训练出的模型**：查看 `models/registry/`。最终生成的 **ONNX** 格式模型会存放在这里，用于边缘端部署。
*   **实验指标与日志**：运行 `mlflow ui`，在浏览器中查看超参数对比、Loss 曲线及模型版本。
*   **物理动作验证**：在没有硬件时，直接查看 `main.py` 运行后的终端输出（Mock 模式）。

### 3. 核心运行流程

1.  **系统入口**：`main.py`。它负责初始化 `sensors`、`brain` 和 `hardware` 这三个核心模块，并启动循环。
2.  **配置中心**：`config.yaml`。在这里切换 **Mock 模式** 或修改 **串口号**，无需改动源码。
3.  **自动化流水线**：使用 `zenml pipeline run` 执行 `pipelines/` 下的任务。

### 4. 如何运行 (Quick Start)

在项目根目录下，使用终端执行：

```powershell
# 1. 激活环境 (Windows)
.\venv\Scripts\activate

# 2. 运行主交互程序 (带硬件 Mock)
python main.py

# 3. 运行 MLOps Demo 演示
python pipelines/demo_mlops.py
```

---

**建议**：在开始编写任何业务代码前，先尝试运行 `main.py` 确保 Mock 环境跑通。
