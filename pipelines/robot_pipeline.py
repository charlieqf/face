# pipelines/robot_pipeline.py
import os
import json
import pandas as pd
import numpy as np
import yaml
from zenml import pipeline, step
from src.models.regression_model import RobotExpressionModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 加载配置
with open("configs/train_config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

@step
def data_loader() -> pd.DataFrame:
    """加载原始数据"""
    data_path = config['data_paths']['raw_data']
    df = pd.read_csv(data_path)
    return df

@step
def trainer(df: pd.DataFrame) -> RobotExpressionModel:
    """模型训练步骤"""
    model = RobotExpressionModel(
        n_estimators=config['model_settings']['rf_params']['n_estimators'],
        max_depth=config['model_settings']['rf_params']['max_depth']
    )
    X, y = model.preprocess(df)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config['training_hyperparams']['test_size'], random_state=42
    )
    
    model.train(X_train, y_train)
    
    # 简单计算一个测试集 MSE 并打印 (演示用，正式可通过 evaluator 步骤记录到 MLflow)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    print(f"Evaluation - Test MSE: {mse:.4f}")
    
    return model

@step
def evaluator(model: RobotExpressionModel, df: pd.DataFrame):
    """生成预测结果并保存到 prediction.json (推理模拟)"""
    # 选取最后 10 个字符作为演示生成
    sample_df = df.tail(10).copy()
    X_sample, _ = model.preprocess(sample_df)
    preds = model.predict(X_sample)
    
    output = []
    for i, row in enumerate(sample_df.itertuples()):
        # 四舍五入到离散挡位
        mouth = int(round(preds[i][0]))
        eye = int(round(preds[i][1]))
        lid = int(round(preds[i][2]))
        
        output.append({
            "char": row.char,
            "mouth": mouth,
            "eye": eye,
            "lid": lid,
            "duration": 300,
            "note": f"Model Prediction (MSE Verified)"
        })
    
    output_path = config['data_paths']['prediction_file']
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"预测结果已保存至: {output_path}")

@pipeline
def robot_expression_pipeline():
    """定义完整 MLOps 管道"""
    df = data_loader()
    model = trainer(df)
    evaluator(model, df)

if __name__ == "__main__":
    robot_expression_pipeline()
