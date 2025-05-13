import numpy as np
from joblib import load


def divide_learning_style():

    # 加载模型
    model = load("student_learning_style_model.pkl")

    # 构造一个学生的特征数据
    # 输入示例 ['task_0_ratio'（任务类型0在全部中的占比）, 'task_1_ratio'（任务类型2在全部中的占比）, 'task_2_ratio', 'task_3_ratio', 'task_4_ratio',
    #      'task_5_ratio', 'average_study_time'（平均学习时间）, 'course_completion_rate'（课程完成率）,
    #      'study_time_21_6_ratio'（在21-6时学习的概率）, 'study_time_7_20_ratio'（在7-20时学习的概率）]
    # 任务类型 (0=图文，1=视频，2=音频，3=讨论，4=文档，5=PPT)
    new_data = np.array([
        [0, 0.40625, 0, 0, 0, 0.40625, 1120.057142857143, 0.9142857142857143, 0.9142857142857143, 0.08571428571428572]
    ])

    # 预测
    prediction = model.predict(new_data)

    # 输出
    print("预测结果：", prediction)
    # 输出示例 预测结果： [[0 0 0]]
    # 按照学习时间段分布：深夜学习型【0】，日间学习型【1】，全时段学习型【2】
    # 按照任务类型分布：视觉导向型【0】，听觉导向型【1】，读写导向型【2】，多元导向型【3】
    # 按照学习时长和完成率分布：高效学习型【0】，低效学习型【1】

divide_learning_style()