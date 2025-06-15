from calculate import get_full_student_profile
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score
import joblib
import os
from typing import List, Dict


class StudentClusterModel:
    def __init__(self):
        """初始化聚类模型"""
        self.kmeans = None
        self.scaler = None
        self.feature_names = None
        self.cluster_profiles = None
        self.best_k = None

    def prepare_features(self, student_ids: List[str], current_date: str) -> pd.DataFrame:
        """
        构建特征矩阵
        """
        features_list = []

        for student_id in student_ids:
            try:
                profile = get_full_student_profile(student_id, current_date).iloc[0].to_dict()

                features = {
                    'student_id': student_id,
                    'answer_count': profile.get('answer_count', 0),
                    'correct_rate': profile.get('correct_rate', 0),
                    'last_7_days_answer_count': profile.get('last_7_days_answer_count', 0),
                    'total_study_time': profile.get('total_study_time', 0),
                    'avg_study_time': profile.get('avg_study_time', 0),
                    'completed_task_count': profile.get('completed_task_count', 0),
                    'completion_rate': profile.get('completion_rate', 0),
                    'task_type_count': profile.get('task_type_count', 0),


                    'morning_study_ratio': profile.get('study_time_ratio', {}).get('8-18', 0),
                    'evening_study_ratio': profile.get('study_time_ratio', {}).get('18-24', 0),
                    'video_audio_ratio': sum(v for k, v in profile.get('task_type_ratio', {}).items()
                                             if str(k) in ['1', '2']),
                    'text_ratio': sum(v for k, v in profile.get('task_type_ratio', {}).items()
                                      if str(k) in ['0', '4', '5']),
                    'discuss_ratio': profile.get('task_type_ratio', {}).get('3', 0)
                }
                features_list.append(features)
            except Exception as e:
                print(f"处理学生 {student_id} 时出错: {str(e)}")
                continue

        return pd.DataFrame(features_list)

    def determine_optimal_clusters(self, student_ids: List[str], current_date: str,
                                   max_clusters: int = 10) -> int:
        """
        确定最佳聚类数
        """
        features_df = self.prepare_features(student_ids, current_date)
        n_samples = len(features_df)

        if n_samples < 2:
            raise ValueError("需要至少2个样本才能聚类")

        max_clusters = min(max_clusters, n_samples - 1)
        if max_clusters < 2:
            return 2

        numeric_cols = [col for col in features_df.columns
                        if col != 'student_id' and pd.api.types.is_numeric_dtype(features_df[col])]
        X = features_df[numeric_cols]

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        ch_scores = []
        db_scores = []
        k_values = range(2, max_clusters + 1)

        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)

            ch_scores.append(calinski_harabasz_score(X_scaled, labels))
            db_scores.append(davies_bouldin_score(X_scaled, labels))

        def normalize(scores):
            return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))

        norm_ch = normalize(np.array(ch_scores))
        norm_db = 1 - normalize(np.array(db_scores))

        combined_scores = 0.7 * norm_ch + 0.3 * norm_db
        best_k = k_values[np.argmax(combined_scores)]
        self.best_k = best_k

        print(f"确定最佳聚类数: {best_k}")
        print(f"Calinski-Harabasz指数: {ch_scores[best_k - 2]:.3f}")
        print(f"Davies-Bouldin指数: {db_scores[best_k - 2]:.3f}")

        return best_k

    def train(self, student_ids: List[str], current_date: str,
              n_clusters: int = None) -> 'StudentClusterModel':
        """
        训练聚类模型
        """
        features_df = self.prepare_features(student_ids, current_date)
        n_samples = len(features_df)

        if n_samples < 2:
            raise ValueError("需要至少2个样本才能训练模型")

        numeric_cols = [col for col in features_df.columns
                        if col != 'student_id' and pd.api.types.is_numeric_dtype(features_df[col])]
        X = features_df[numeric_cols]
        self.feature_names = numeric_cols

        if self.scaler is None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)

        if n_clusters is None:
            if self.best_k is None:
                print("自动确定最佳聚类数...")
                n_clusters = min(3, n_samples)
            else:
                n_clusters = self.best_k
        else:
            n_clusters = min(n_clusters, n_samples)

        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.kmeans.fit(X_scaled)

        features_df['cluster'] = self.kmeans.labels_
        self.cluster_profiles = features_df.groupby('cluster')[self.feature_names].mean()

        print("\n聚类中心特征:")
        print(self.cluster_profiles)

        self.evaluate_model(student_ids, current_date)

        return self

    def evaluate_model(self, student_ids: List[str], current_date: str) -> Dict[str, float]:
        """
        评估模型性能
        """
        if self.kmeans is None:
            raise ValueError("模型未训练")

        features_df = self.prepare_features(student_ids, current_date)
        X = features_df[self.feature_names]
        X_scaled = self.scaler.transform(X)
        labels = self.kmeans.predict(X_scaled)

        metrics = {
            'n_clusters': len(np.unique(labels)),
            'calinski_harabasz_score': calinski_harabasz_score(X_scaled, labels),
            'davies_bouldin_score': davies_bouldin_score(X_scaled, labels),
            'inertia': self.kmeans.inertia_
        }

        print("\n模型评估结果:")
        print(f"- 聚类数: {metrics['n_clusters']}")
        print(f"- Calinski-Harabasz指数: {metrics['calinski_harabasz_score']:.3f} (越大越好)")
        print(f"- Davies-Bouldin指数: {metrics['davies_bouldin_score']:.3f} (越小越好)")
        print(f"- 簇内平方和: {metrics['inertia']:.3f}")

        return metrics

    def predict(self, student_id: str, current_date: str) -> int:
        """
        预测单个学生的聚类
        """
        if self.kmeans is None:
            raise ValueError("模型未训练")

        features = self.prepare_features([student_id], current_date)
        if len(features) == 0:
            return -1

        X = features[self.feature_names]
        X_scaled = self.scaler.transform(X)
        return self.kmeans.predict(X_scaled)[0]

    def batch_predict(self, student_ids: List[str], current_date: str) -> pd.DataFrame:
        """
        批量预测学生聚类
        """
        features_df = self.prepare_features(student_ids, current_date)
        if len(features_df) == 0:
            return pd.DataFrame(columns=['student_id', 'cluster'])

        X = features_df[self.feature_names]
        X_scaled = self.scaler.transform(X)
        features_df['cluster'] = self.kmeans.predict(X_scaled)
        return features_df[['student_id', 'cluster']]

    def save_model(self, path: str = 'student_cluster_model'):
        """保存模型到指定路径"""
        if not os.path.exists(path):
            os.makedirs(path)

        joblib.dump({
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'cluster_profiles': self.cluster_profiles,
            'best_k': self.best_k
        }, os.path.join(path, 'model.pkl'))

    @classmethod
    def load_model(cls, path: str = 'student_cluster_model'):
        """从指定路径加载模型"""
        model = cls()
        data = joblib.load(os.path.join(path, 'model.pkl'))

        model.kmeans = data['kmeans']
        model.scaler = data['scaler']
        model.feature_names = data['feature_names']
        model.cluster_profiles = data['cluster_profiles']
        model.best_k = data['best_k']

        return model


if __name__ == "__main__":
    try:
        # student_ids = ['1840780744500391936', '1840348588070490112','1839664954161143808','1840791550193479680'
        #                '1840652674042343424', '1838028838184222720','1839622224867188736','1840389333774417920'
        #                '1840785811651891200','1840640557005955072','1840679067618435072','1840789869398786048'
        #                '1840771656241160192','1840782850779967488','1840679067618435072']
        current_date = '2024-10-11 00:00:00'
        #
        # model = StudentClusterModel()
        #
        # features_df = model.prepare_features(student_ids, current_date)
        # print("\n学生特征:")
        # features_df.to_csv('学生特征.csv', index=False)  # index=False 表示不保存行索引
        # print(features_df)
        #
        #
        # best_k = model.determine_optimal_clusters(student_ids, current_date)
        #
        # print("\n训练模型中...")
        # model.train(student_ids, current_date, n_clusters=best_k)
        #
        # # 保存模型
        # model.save_model()

        # 加载模型
        loaded_model = StudentClusterModel.load_model()

        # 预测
        new_student = '1838028838184222720'
        cluster = loaded_model.predict(new_student, current_date)
        print(f"\n预测结果: 学生 {new_student} 属于聚类 {cluster}")

    except Exception as e:
        print(f"程序运行出错: {str(e)}")
