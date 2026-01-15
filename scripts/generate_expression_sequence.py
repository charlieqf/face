# scripts/generate_expression_sequence.py
import pandas as pd
import numpy as np

np.random.seed(2026)
n_frames = 50
data = pd.DataFrame({
    'timestamp': np.arange(n_frames) * 0.1, # 每帧 0.1 秒
    'jawOpen': np.clip(np.random.randn(n_frames) * 0.3 + 0.3, 0, 1),
    'eyeBlinkLeft': np.clip(np.random.randn(n_frames) * 0.1, 0, 1),
    'eyeBlinkRight': np.clip(np.random.randn(n_frames) * 0.1, 0, 1),
})
data.to_csv('data/expression_sequence_v1.csv', index=False)
print("Generated data/expression_sequence_v1.csv")
