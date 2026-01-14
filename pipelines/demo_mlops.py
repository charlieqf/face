import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from zenml import pipeline, step
import mlflow
import os

# 模拟 DVC 获取数据
@step
def load_data() -> pd.DataFrame:
    """模拟从 DVC 跟踪的 CSV 文件加载数据"""
    if not os.path.exists("data.csv"):
        # 创建模拟数据: 
        # 输入: 音量 (0-100)
        # 目标: 嘴等级(1-5), 眼球位置(1-21), 眼皮状态(1-4)
        np.random.seed(42)
        n_samples = 100
        data = pd.DataFrame({
            'volume': np.random.randint(0, 100, n_samples),
            'mouth_target': np.random.randint(1, 6, n_samples),
            'eye_target': np.random.randint(1, 22, n_samples),
            'lid_target': np.random.randint(1, 5, n_samples)
        })
        data.to_csv("data.csv", index=False)
        print("Created synthetic data.csv with multiple targets.")
    
    return pd.read_csv("data.csv")

@step(experiment_tracker="mlflow_tracker")
def train_models(df: pd.DataFrame) -> dict:
    """训练多个简单的模型，并记录指标"""
    targets = ['mouth_target', 'eye_target', 'lid_target']
    models = {}
    
    X = df[['volume']]
    
    print("\n--- Training Progress ---")
    for t in targets:
        y = df[t]
        model = LinearRegression()
        model.fit(X, y)
        models[t] = model
        
        # 记录到 MLflow
        mse = mean_squared_error(y, model.predict(X))
        mlflow.log_metric(f"{t}_mse", mse)
        print(f"Model for {t} trained. MSE: {mse:.4f}")
    
    return models

@step
def generate_hardware_commands(models: dict, df: pd.DataFrame):
    """根据预测结果生成全套硬件 TTL 指令"""
    X_test = df[['volume']].iloc[:3]  # 取前 3 条演示
    
    print("\n--- 硬件指令全映射演示 (Full Hardware Command Mapping) ---")
    for i in range(len(X_test)):
        vol = X_test.iloc[i]['volume']
        input_data = X_test.iloc[[i]]
        
        # 1. 嘴部映射 (#DGM:1-5!)
        mouth_pred = models['mouth_target'].predict(input_data)[0]
        mouth_cmd = f"#DGM:{int(np.clip(np.round(mouth_pred), 1, 5))}!"
        
        # 2. 眼球映射 ($DGB:1-21!)
        eye_pred = models['eye_target'].predict(input_data)[0]
        eye_cmd = f"$DGB:{int(np.clip(np.round(eye_pred), 1, 21))}!"
        
        # 3. 眼皮映射 ($DGL:1-4!)
        lid_pred = models['lid_target'].predict(input_data)[0]
        lid_cmd = f"$DGL:{int(np.clip(np.round(lid_pred), 1, 4))}!"
        
        print(f"【样本 {i+1}】输入音量: {vol}")
        print(f"  └─ 嘴部指令: {mouth_cmd}  (预测: {mouth_pred:.2f})")
        print(f"  └─ 眼球指令: {eye_cmd}  (预测: {eye_pred:.2f})")
        print(f"  └─ 眼皮指令: {lid_cmd}  (预测: {lid_pred:.2f})")

@pipeline
def robot_expression_pipeline():
    """定义完整表情训练管道"""
    data = load_data()
    models = train_models(data)
    generate_hardware_commands(models, data)

if __name__ == "__main__":
    robot_expression_pipeline()
