# DVC 数据版本控制指引

在我们的机器人项目中，音频、sEMG 信号数据以及训练好的模型产出通常体积较大。为了保持 Git 仓库的轻量化，我们使用 **DVC (Data Version Control)** 进行数据管理。

## 1. 核心概念

*   **数据不进 Git**：实际的 `.csv` 或 `.onnx` 文件由 DVC 存储，Git 仅记录对应的 `.dvc` 指针文件。
*   **Pipeline 自动化**：通过 `dvc.yaml` 定义数据处理流程，确保从原始数据到最终模型的每一步都是可追溯、可复现的。

## 2. dvc.yaml 深度解析

项目根目录下的 [dvc.yaml](file:///c:/work/code/face/dvc.yaml) 是项目的“流水线脚本”。

```yaml
stages:
  preprocess:                # 阶段名称：预处理
    cmd: python src/sensors/audio_processor.py  # 执行的命令
    deps:                    # 依赖项
      - data/raw             # 如果 raw 目录下的文件变了，此阶段需重新运行
    outs:                    # 输出项
      - data/processed       # 预处理后的特征数据

  train:                     # 阶段名称：训练
    cmd: python pipelines/demo_mlops.py
    deps:
      - data/processed       # 依赖上一步的输出
    outs:
      - models/registry      # 输出最终模型
```

## 3. 常用操作命令

### 获取/同步数据
当你第一次克隆项目或另一台电脑上传了新模型时：
```powershell
dvc pull
```

### 运行流水线 (唯一推荐方式)
不要手动运行 `python scripts/xxx.py`。请使用以下命令，DVC 会自动检查哪些环节需要更新：
```powershell
dvc repro
```
*   如果依赖项没有变化，DVC 会直接从缓存跳过该阶段，极大地节省时间。

### 跟踪新数据
如果你手动在 `data/raw/` 放入了新文件：
```powershell
# 添加跟踪
dvc add data/raw/new_data.csv

# 提交指针文件到 Git
git add data/raw/new_data.csv.dvc .gitignore
git commit -m "Add new raw sensor data"
```

### 查看流水线拓扑
```powershell
dvc dag
```
这会以图形方式展示数据流向。

## 4. 协作注意事项

1.  **千万不要 git add 大文件**：如果不小心把大文件存入了 Git，请及时回滚。
2.  **修改脚本后 repro**：如果你修改了 `src/` 下的代码逻辑，记得运行 `dvc repro` 重新生成下游产出。
3.  **推送数据**：完成本地实验后，记得 `dvc push` 将数据同步到云端/共享存储。

---

**下一步**：在开始训练你的模型前，请确保已经执行了 `zenml init` 和 `dvc init`。
