# src/models/regression_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class RobotExpressionModel:
    def __init__(self, n_estimators=100, max_depth=10, random_state=42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        self.label_encoder = LabelEncoder()
        self.is_trained = False

    def preprocess(self, df):
        """处理字符特征和情绪特征"""
        # 为字符编号
        df['char_code'] = self.label_encoder.fit_transform(df['char'].astype(str))
        # 为情绪编号
        emotion_map = {'positive': 1, 'negative': -1, 'neutral': 0, 'surprise': 2}
        df['emotion_code'] = df['emotion'].map(emotion_map).fillna(0)
        
        X = df[['char_code', 'emotion_code']]
        y = df[['mouth_target', 'eye_target', 'lid_target']]
        return X, y

    def train(self, X, y):
        print(f"开始训练随机森林模型... 样本量: {len(X)}")
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            raise ValueError("模型尚未训练！")
        return self.model.predict(X)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'encoder': self.label_encoder
        }, path)

    @classmethod
    def load(cls, path):
        data = joblib.load(path)
        instance = cls()
        instance.model = data['model']
        instance.label_encoder = data['encoder']
        instance.is_trained = True
        return instance
