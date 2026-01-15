# 第二天工作指南：表情序列设计与模拟播放

今天的目标是理解"文本→表情序列"的核心概念，并在**无硬件**环境下构建完整的模拟验证系统。

> [!IMPORTANT]
> **核心概念**：机器人说话时，每个字/词对应一组 **(嘴巴, 眼球, 眼皮)** 的联合状态。这个"文本→表情序列"的映射正是我们 MLOps 平台要训练的模型目标。

> [!NOTE]
> **与正式采集训练的关系**
> 
> 今天的手动设计是正式训练的**简化预演**：
> 
> | 方面 | 今天的练习 | 正式训练 |
> |------|-----------|----------|
> | 输入源 | 文本字符 | 音频波形 / ARKit / sEMG 传感器 |
> | 标注方式 | 人工设计 | 真人表演时自动采集 |
> | 输出格式 | `(mouth, eye, lid)` 三元组 | **完全相同** |
> 
> **为什么要手动设计？**
> 1. 理解 `(mouth, eye, lid)` 三元组如何表达情感
> 2. 熟悉数据格式，为后续处理真实数据做准备
> 3. 积累"什么样的表情看起来自然"的直觉
> 4. 你今天创建的 CSV 格式，与将来 ML 模型的训练标签格式**完全一致**

---

## 任务 1：理解表情三元组

### 硬件状态回顾
参照 [TTL控制指令](file:///c:/work/code/face/docs/hardware/ttl%E6%8E%A7%E5%88%B6%E6%8C%87%E4%BB%A4.md)：

| 部件 | 指令格式 | 取值范围 | 说明 |
|------|----------|----------|------|
| 嘴巴 | `#DGM:N!` | 1-5 | 1=闭嘴, 5=完全张开 |
| 眼球 | `$DGB:N!` | 1-21 | 见眼球运动图 |
| 眼皮 | `$DGL:N!` | 1-4 | 1=正常, 2=眯眼, 3=闭眼, 4=瞪眼 |

### 表情三元组定义
每个时刻的机器人表情可以用一个三元组表示：
```
(mouth, eye, lid) = (嘴巴档位, 眼球位置, 眼皮状态)
```

例如：`(3, 11, 1)` 表示"嘴巴半开、眼球居中、正常睁眼"

---

## 任务 2：手动设计表情序列

### 2.1 选择一段示例文本
```
"你好，我是机器人小白。"
```

### 2.2 为每个字设计表情三元组

请在 `data/` 目录下创建 `expression_sequence_manual.csv`：

```csv
char,mouth,eye,lid,note
你,3,11,1,普通发音
好,4,11,1,张嘴较大
，,1,11,1,停顿闭嘴
我,3,10,1,眼球微左
是,3,12,1,眼球微右
机,3,11,1,
器,3,11,1,
人,4,11,1,
小,2,11,2,眯眼表示亲切
白,4,11,1,
。,1,11,3,结束时闭眼
```

### 2.3 设计原则
- **嘴巴**：开口音(啊、哦)用 4-5，闭口音(不、木)用 1-2，一般用 3
- **眼球**：正常居中(11)，偶尔左右移动增加生动感
- **眼皮**：正常说话用 1，强调/微笑用 2(眯眼)，结束/思考用 3(闭眼)

---

## 任务 3：创建表情序列播放器

请创建 `scripts/expression_player.py`：

```python
# scripts/expression_player.py
"""
表情序列播放器 - 读取 CSV 并逐帧发送 TTL 指令
"""
import sys
import time
import pandas as pd
sys.path.insert(0, '.')

from src.hardware.robot_controller import RobotController

def play_expression_sequence(csv_path: str, delay: float = 0.3):
    """
    播放表情序列
    
    Args:
        csv_path: CSV 文件路径，包含 char, mouth, eye, lid 列
        delay: 每帧间隔秒数
    """
    robot = RobotController(mock=True)
    df = pd.read_csv(csv_path)
    
    print("=" * 60)
    print("表情序列播放开始")
    print("=" * 60)
    print(f"{'字符':<4} {'嘴巴':<6} {'眼球':<6} {'眼皮':<6} TTL指令")
    print("-" * 60)
    
    for _, row in df.iterrows():
        char = row['char']
        mouth = int(row['mouth'])
        eye = int(row['eye'])
        lid = int(row['lid'])
        
        # 发送指令
        robot.set_mouth(mouth)
        robot.set_eye_position(eye)
        robot.set_eyelid(lid)
        
        # 显示当前帧
        print(f"{char:<4} {mouth:<6} {eye:<6} {lid:<6}", end="")
        print(f"#DGM:{mouth}! $DGB:{eye}! $DGL:{lid}!")
        
        time.sleep(delay)
    
    print("=" * 60)
    print("播放结束")
    robot.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='播放表情序列')
    parser.add_argument('csv', nargs='?', default='data/expression_sequence_manual.csv',
                        help='CSV 文件路径')
    parser.add_argument('--delay', type=float, default=0.3, help='帧间隔(秒)')
    args = parser.parse_args()
    
    play_expression_sequence(args.csv, args.delay)
```

### 运行验证
```powershell
python scripts/expression_player.py
```

预期输出：
```
============================================================
表情序列播放开始
============================================================
字符  嘴巴    眼球    眼皮    TTL指令
------------------------------------------------------------
你    3       11      1       #DGM:3! $DGB:11! $DGL:1!
好    4       11      1       #DGM:4! $DGB:11! $DGL:1!
，    1       11      1       #DGM:1! $DGB:11! $DGL:1!
...
============================================================
播放结束
```

---

## 任务 4：扩展练习

### 4.1 设计不同情绪的表情序列
创建多个 CSV 文件，表达不同情绪：

| 文件名 | 文本内容 | 情绪特点 |
|--------|----------|----------|
| `happy.csv` | "太开心了！" | 嘴巴常开(4-5)，眯眼(2) |
| `sad.csv` | "好难过..." | 嘴巴微开(2-3)，眼皮下垂感 |
| `surprised.csv` | "真的吗？" | 瞪眼(4)，嘴巴大开(5) |

### 4.2 思考：如何自动化？
完成手动标注后，思考以下问题（记录在笔记中）：

1. 如果有 1000 句话要标注，如何提高效率？
2. 能否根据拼音/音素自动推断嘴巴开合？
3. 眼球和眼皮的变化是否可以用规则生成？

这些问题的答案将指导**第三阶段**的 ML 模型训练方向。

---

## 任务 5（可选）：研究 Voice_Driven_Humanoid_Head

如果时间充裕，可以开始分析 [Voice_Driven_Humanoid_Head](https://github.com/acromtech/Voice_Driven_Humanoid_Head)：
- 它是如何触发嘴巴动作的？
- 是逐字/逐词，还是基于音量？
- 我们能否借鉴其逻辑？

---

## 今日成果检查

完成以下内容即视为第二天任务达成：

- [ ] 创建了 `data/expression_sequence_manual.csv`，包含至少 10 个字符的标注
- [ ] `scripts/expression_player.py` 能正确读取并播放序列
- [ ] （可选）创建了 1-2 个不同情绪的表情序列
- [ ] 记录了"如何自动化"的思考笔记

---

## 参考文档
- [第一天工作指南](file:///c:/work/code/face/docs/guides/work_guide_day1.md)
- [TTL 控制指令](file:///c:/work/code/face/docs/hardware/ttl%E6%8E%A7%E5%88%B6%E6%8C%87%E4%BB%A4.md)
- [眼球运动位置图](file:///c:/work/code/face/docs/hardware/%E7%9C%BC%E7%90%83%E8%BF%90%E5%8A%A8.png)
