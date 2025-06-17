import joblib
import os
import numpy as np


def load_model(path: str = 'student_cluster_model'):
    """从指定路径加载模型"""
    data = joblib.load(os.path.join(path, 'model.pkl'))

    kmeans = data['kmeans']
    scaler = data['scaler']
    feature_names = data['feature_names']
    cluster_profiles = data['cluster_profiles']
    best_k = data['best_k']

    return {
        'kmeans': kmeans,
        'scaler': scaler,
        'feature_names': feature_names,
        'cluster_profiles': cluster_profiles,
        'best_k': best_k
    }

# 使用示例
model_data = load_model()
kmeans = model_data['kmeans']
scaler = model_data['scaler']

# # 准备预测数据（假设你有待预测的特征数据）
# X_new = [...]  # 你的新数据特征
# # 数据标准化
# X_new_scaled = scaler.transform(X_new)
# # 进行聚类预测
# predictions = kmeans.predict(X_new_scaled)
# # 如果需要获取聚类中心距离
# distances = kmeans.transform(X_new_scaled)





import pandas as pd
# 读取 CSV 文件
df = pd.read_csv('学生特征.csv')

feature_names = [
    # 'student_id',
    'answer_count',
    'correct_rate',
    'last_7_days_answer_count',
    'total_study_time',
    'avg_study_time',
    'completed_task_count',
    'completion_rate',
    'task_type_count',
    'morning_study_ratio',
    'evening_study_ratio',
    'video_audio_ratio',
    'text_ratio',
    'discuss_ratio'
]


X = df[feature_names]
X_scaled = scaler.transform(X)
result=kmeans.predict(X_scaled)

print(f"df:\n{df}")

#把所属分类 加入df中，并保存为csv文件
df['cluster'] = result
df.to_csv('学生特征分类.csv', index=False)


for i in range(len(result)):
    print(f"学生 {df['student_id'].iloc[i]} 属于第 {result[i]} 类")
# print(f"self.best_k:{sbest_k}")

