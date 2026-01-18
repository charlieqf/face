# scripts/generate_dataset_v2.py
"""
工业级表情数据集生成器 - 针对“机器人直播”场景
逻辑：输入文本词库 -> 模拟人类表情规律 -> 产出 (Text, Seq) 样本对
"""
import pandas as pd
import numpy as np
import os
import json

# 语义-情绪基础映射 (模拟面部传感器标注逻辑)
EMOTION_RULES = {
    'positive': {'mouth_range': (3, 5), 'eye_range': (10, 12), 'lid_range': (1, 2)},
    'negative': {'mouth_range': (1, 2), 'eye_range': (16, 21), 'lid_range': (2, 3)},
    'neutral':  {'mouth_range': (1, 3), 'eye_range': (11, 11), 'lid_range': (1, 1)},
    'surprise': {'mouth_range': (4, 5), 'eye_range': (1, 5),   'lid_range': (4, 4)}
}

WORDS_BANK = {
    'positive': ["你好", "太棒了", "今天心情很好", "谢谢大家的支持", "欢迎来到直播间"],
    'negative': ["对不起", "有点难过", "情况不太好", "请不要这样", "唉"],
    'neutral':  ["这是一段测试", "接下来我们看", "机器人正在运行", "准备好了吗", "好的"],
    'surprise': ["哇", "真的吗", "天哪", "不可思议", "快看"]
}

def generate_sentence_sequence(seq_id, text, emotion):
    """为一句话生成对应的动作序列"""
    rules = EMOTION_RULES[emotion]
    rows = []
    
    # 模拟 30fps 或 字符级步进 (直播场景常按字符/停顿步进)
    for i, char in enumerate(text):
        mouth = np.random.randint(rules['mouth_range'][0], rules['mouth_range'][1] + 1)
        eye = np.random.randint(rules['eye_range'][0], rules['eye_range'][1] + 1)
        lid = np.random.randint(rules['lid_range'][0], rules['lid_range'][1] + 1)
        
        # 增加一点随机扰动 (即传感器噪声)
        if np.random.rand() > 0.8:
            eye = np.clip(eye + np.random.randint(-1, 2), 1, 21)
            
        rows.append({
            'sequence_id': seq_id,
            'char': char,
            'mouth_target': mouth,
            'eye_target': eye,
            'lid_target': lid,
            'emotion': emotion,
            'timestamp': round(i * 0.3, 2) # 假设每个字 300ms
        })
    
    # 在句子结尾添加一个短暂的闭嘴停顿
    rows.append({
        'sequence_id': seq_id, 'char': ' ', 'mouth_target': 1, 'eye_target': 11, 'lid_target': 1, 
        'emotion': 'neutral', 'timestamp': round((len(text)) * 0.3, 2)
    })
    
    return rows

def main(n_samples=2000):
    print(f"正在生成 {n_samples} 条直播场景样本数据...")
    all_data = []
    
    for i in range(n_samples):
        emotion = np.random.choice(list(WORDS_BANK.keys()))
        text = np.random.choice(WORDS_BANK[emotion])
        # 随机拼接一两句话增加多样性
        if np.random.rand() > 0.7:
            text += "，" + np.random.choice(WORDS_BANK['neutral'])
            
        seq = generate_sentence_sequence(i, text, emotion)
        all_data.extend(seq)
    
    df = pd.DataFrame(all_data)
    
    # 确保目录存在
    os.makedirs('data/raw', exist_ok=True)
    
    output_path = 'data/raw/training_data.csv'
    df.to_csv(output_path, index=False)
    print(f"数据生成完成！保存至: {output_path}")
    print(f"总帧数: {len(df)}")
    print(f"预览:\n{df.head()}")

if __name__ == "__main__":
    main(2000) # 先生成 2000 条 PoC 样本
