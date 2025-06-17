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
        # features_df = self.prepare_features(student_ids, current_date)
        features_df = pd.read_csv('学生特征.csv')
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
        student_ids = [
            '1830475870539571200',
            '1832033949675745280',
            '1832026288704348160',
            '1832021769843257344',
            '1832017802530267136',
            '1832012553951920128',
            '1832007618803863552',
            '1832047936687882240',
            '1832012456768262144',
            '1833416659428708352',
            '1830977039874707456',
            '1830480741170896896',
            '1831156500607430656',
            '1830561109808181248',
            '1830469455951114240',
            '1833416575449964544',
            '1833069629734694912',
            '1830999931839729664',
            '1830475922060009472',
            '1833419087449985024',
            '1833417244122861568',
            '1831664841339748352',
            '1833416735857881088',
            '1833417038969327616',
            '1833416547865755648',
            '1833416604796256256',
            '1833416577641025536',
            '1833416558418087936',
            '1831663398015692800',
            '1831593870795104256',
            '1833419043519221760',
            '1833416536231460864',
            '1833417213800525824',
            '1833418682937298944',
            '1833418566477852672',
            '1830438025996193792',
            '1830441557972815872',
            '1830436646232592384',
            '1831189606152830976',
            '1831232602171711488',
            '1831187971830542336',
            '1831185997193986048',
            '1830610324656680960',
            '1831483267499606016',
            '1831141142106476544',
            '1834470398130946048',
            '1834530962149761024',
            '1834611829222809600',
            '1834766655904763904',
            '1834799267023249408',
            '1834893180233981952',
            '1834474275883454464',
            '1834580813180235776',
            '1833755291674632192',
            '1831141453566144512',
            '1833756442249445376',
            '1832009797561245696',
            '1831997261424173056',
            '1831873489206038528',
            '1830997310718656512',
            '1830474383646146560',
            '1831868188565073920',
            '1831907326513672192',
            '1831624234634493952',
            '1831593869902135296',
            '1831872510074351616',
            '1833418274158624768',
            '1833016200501477376',
            '1830982392000073728',
            '1830605197509152768',
            '1833416597289717760',
            '1833416481544421376',
            '1833416783936319488',
            '1833417463583105024',
            '1831154316926525440',
            '1831262449589608448',
            '1831141217138827264',
            '1833756719501598720',
            '1831156093811351552',
            '1830437134178656256',
            '1830470907536871424',
            '1833418684994859008',
            '1831280243019108352',
            '1831227580339331072',
            '1834499752382353408',
            '1831593886285897728',
            '1833416487255056384',
            '1833416597317824512',
            '1833416649803108352',
            '1833416794427363328',
            '1833416546614644736',
            '1830483857157005312',
            '1833755698656739328',
            '1831142340565803008',
            '1831143491454844928',
            '1830465570820009984',
            '1833416703469965312',
            '1834529105422807040',
            '1834940308167503872',
            '1831875685700554752',
            '1830613182757629952',
            '1830577343728283648',
            '1832018522488086528',
            '1833416827197632512',
            '1831610344574558208',
            '1830561264520335360',
            '1830613969192165376',
            '1830768959145177088',
            '1835248495969869824',
            '1831141597810298880',
            '1833416606010904576',
            '1831151187904630784',
            '1830880764864192512',
            '1830413023804141568',
            '1830414423796838400',
            '1830470937311768576',
            '1830413617376468992',
            '1830910996910002176',
            '1830499683828768768',
            '1830465682758483968',
            '1831307285386788864',
            '1833757917642715136',
            '1831485765394268160',
            '1830815464396476416',
            '1830823975166332928',
            '1831615363568128000',
            '1832781825422790656',
            '1831663943178960896',
            '1831652031230046208',
            '1833417011127324672',
            '1833418200936308736',
            '1830604685129306112',
            '1830412337057943552',
            '1834437257740865536',
            '1831480754499825664',
            '1831141252207964160',
            '1833755436020056064',
            '1831154453861511168',
            '1831593134423564288',
            '1831154415693508608',
            '1831142292729630720',
            '1831187466998927360',
            '1833756006842187776',
            '1831188743280590848',
            '1831198821421240320',
            '1831154478683078656',
            '1831622514513039360',
            '1838831158287421440',
            '1831157595961774080',
            '1835125857285259264',
            '1830811920444166144',
            '1830468126066630656',
            '1831141254659645440',
            '1830828787686363136',
            '1830964157704261632',
            '1833418174470598656',
            '1831663439799336960',
            '1833417433195913216',
            '1833755433860251648',
            '1831155451204292608',
            '1831142682559864832',
            '1831629195451887616',
            '1830605918083035136',
            '1830441231805722624',
            '1831153376643547136',
            '1831229771517534208',
            '1834784604374372352',
            '1833416681736130560',
            '1831589573523329024',
            '1830868692700647424',
            '1834492369429995520',
            '1834514325491974144',
            '1834935413686984704',
            '1830417583097683968',
            '1830970872014614528',
            '1830864082374107136',
            '1830841563288219648',
            '1831230219417292800',
            '1830413763166515200',
            '1830414943453204480',
            '1833757710926749696',
            '1833755867784998912',
            '1833757627547930624',
            '1833755713383903232',
            '1838825180762685440',
            '1833416160081420288'
        ]

        current_date = '2024-10-11 00:00:00'
        #
        model = StudentClusterModel()
        #
        # features_df = model.prepare_features(student_ids, current_date)
        # print("\n学生特征:")
        # features_df.to_csv('学生特征.csv', index=False)  # index=False 表示不保存行索引
        # print(features_df)


        best_k = model.determine_optimal_clusters(student_ids, current_date)
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
        print(f"self.best_k:{best_k}")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
