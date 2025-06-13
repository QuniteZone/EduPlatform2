import os
from sqlalchemy import text
from datetime import timedelta
import pandas as pd
from sqlalchemy import create_engine


# 查询学生基础信息
def get_student_info(student_id):
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/eduplatform')
    with engine.connect() as conn:
        sql = text("""
            SELECT faculty, administrative_classes, major
            FROM students
            WHERE student_id = :student_id
            LIMIT 1
        """)
        result = conn.execute(sql, {"student_id": student_id}).fetchone()
        if result:
            faculty, class_name, major = result
            return faculty, class_name, major
        else:
            return None, None, None

# 答题数据统计
def get_answer_stats(user_id, current_date):
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/eduplatform?charset=utf8mb4')
    query = f"""
        SELECT user_id, score, review_result, create_time
        FROM answerlog
        WHERE user_id = '{user_id}'
    """
    df = pd.read_sql(query, engine)
    if df.empty:
        return None

    df['create_time'] = pd.to_datetime(df['create_time'])
    df['review_result'] = pd.to_numeric(df['review_result'], errors='coerce').fillna(0).astype(int)

    answer_count = len(df)
    correct_count = (df['review_result'] == 1).sum()
    correct_rate = correct_count / answer_count if answer_count > 0 else 0
    last_active = df['create_time'].max()

    if isinstance(current_date, str):
        current_date = pd.to_datetime(current_date)
    start_date = current_date - timedelta(days=7)
    last_7_days_count = df[(df['create_time'] > start_date) & (df['create_time'] <= current_date)].shape[0]

    return {
        'answer_count': answer_count,
        'correct_rate': correct_rate,
        'last_active': last_active,
        'last_7_days_answer_count': last_7_days_count
    }

# 学习数据统计
def get_study_stats(user_id):
    engine = create_engine("mysql+pymysql://root:123456@localhost:3306/eduplatform?charset=utf8mb4")

    query = f"""
        SELECT create_by, lesson_id, study_time, status, create_time, task_type
        FROM study_recore_task_test
        WHERE create_by = '{user_id}'
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        return f"学生 {user_id} 没有学习记录"

    df["study_time"] = pd.to_numeric(df["study_time"], errors="coerce").fillna(0)
    df["status"] = pd.to_numeric(df["status"], errors="coerce").fillna(0).astype(int)
    df["create_time"] = pd.to_datetime(df["create_time"], errors="coerce")
    df["hour"] = df["create_time"].dt.hour

    total_study_time = df["study_time"].sum()/60
    avg_study_time = df["study_time"].mean()/60

    completed_df = df[df["status"] == 1]
    completed_tasks = len(completed_df)
    completion_rate = completed_tasks / len(df) if len(df) else 0

    def split_task_types(series):
        all_types = []
        for val in series.dropna():
            all_types.extend(val.split(','))
        return all_types

    completed_task_types = split_task_types(completed_df["task_type"])
    task_type_count = len(set(completed_task_types))
    task_type_ratio = pd.Series(completed_task_types).value_counts(normalize=True).sort_index().round(3).to_dict()

    time_8_18 = df[(df["hour"] >= 8) & (df["hour"] < 18)]["study_time"].sum()
    time_18_24 = df[(df["hour"] >= 18) & (df["hour"] < 24)]["study_time"].sum()
    total_time_window = time_8_18 + time_18_24

    time_ratio = {
        "8-18": round(time_8_18 / total_time_window, 3) if total_time_window else 0,
        "18-24": round(time_18_24 / total_time_window, 3) if total_time_window else 0
    }

    return {
        "user_id": user_id,
        "total_study_time": round(total_study_time, 2),
        "avg_study_time": round(avg_study_time, 2),
        "completed_task_count": completed_tasks,
        "task_type_count": task_type_count,
        "task_type_ratio": task_type_ratio,
        "completion_rate": round(completion_rate, 2),
        "study_time_ratio": time_ratio
    }

# 组合学生画像
def get_full_student_profile(user_id, current_date):
    faculty, class_name, major = get_student_info(user_id)
    answer_stats = get_answer_stats(user_id, current_date)
    study_stats = get_study_stats(user_id)

    data = {
        "user_id": user_id,
        "faculty": faculty,
        "major": major,
        "class": class_name
    }

    if answer_stats:
        data.update({
            "answer_count": answer_stats["answer_count"],
            "correct_rate": round(answer_stats["correct_rate"], 3),
            "last_active": answer_stats["last_active"],
            "last_7_days_answer_count": answer_stats["last_7_days_answer_count"]
        })
    else:
        data.update({
            "answer_count": 0,
            "correct_rate": 0,
            "last_active": None,
            "last_7_days_answer_count": 0
        })

    if isinstance(study_stats, dict):
        data.update(study_stats)
    else:
        data["study_stats"] = study_stats

    return pd.DataFrame([data])

# 打标签
import ast

def generate_student_tags(data):
    tags = []

    # 单位转换：秒转分钟
    total_study_time_min = data['total_study_time'] / 60
    avg_study_time_min = data['avg_study_time'] / 60

    recent_answer_count = data['last_7_days_answer_count']
    task_completion_rate = data['completion_rate']

    # task_type_ratio 和 study_time_ratio 可能是字符串，转换为字典
    task_type_ratio = ast.literal_eval(data['task_type_ratio']) if isinstance(data['task_type_ratio'], str) else data['task_type_ratio']
    time_ratio = ast.literal_eval(data['study_time_ratio']) if isinstance(data['study_time_ratio'], str) else data['study_time_ratio']

    task_type_count = data['task_type_count']

    if total_study_time_min > 300:
        tags.append(0)
    elif total_study_time_min >= 100:
        tags.append(1)
    else:
        tags.append(2)

    if recent_answer_count >= 50:
        tags.append(3)
    elif recent_answer_count >= 20:
        tags.append(4)
    else:
        tags.append(5)

    if task_completion_rate >= 0.8:
        tags.append(6)
    elif task_completion_rate >= 0.5:
        tags.append(7)
    else:
        tags.append(8)

    if avg_study_time_min >= 40:
        tags.append(9)
    elif avg_study_time_min >= 20:
        tags.append(10)
    else:
        tags.append(11)

    if time_ratio.get("8-18", 0) >= 0.6:
        tags.append(12)
    elif time_ratio.get("18-24", 0) >= 0.6:
        tags.append(13)
    else:
        tags.append(14)

    video_audio_ratio = sum(v for k, v in task_type_ratio.items() if k in ['1', '2'])
    text_ratio = sum(v for k, v in task_type_ratio.items() if k in ['0', '4', '5'])
    discuss_ratio = task_type_ratio.get('3', 0)

    if video_audio_ratio > 0.5:
        tags.append(15)
    elif text_ratio > 0.5:
        tags.append(16)
    elif discuss_ratio > 0.5:
        tags.append(17)
    else:
        tags.append(18)

    if task_type_count >= 5:
        tags.append(19)
    elif task_type_count >= 3:
        tags.append(20)
    else:
        tags.append(21)

    return tags


# 取学生信息，假设返回DataFrame或Series，转换成字典传入
student_info = get_full_student_profile('1842595446920237056','2024-10-11 00:00:00')

print(student_info.T)

# 转成字典再传入
if hasattr(student_info, "iloc"):  # DataFrame
    student_info_dict = student_info.iloc[0].to_dict()
elif hasattr(student_info, "to_dict"):  # Series
    student_info_dict = student_info.to_dict()
else:
    student_info_dict = student_info  # 本身就是字典

tags = generate_student_tags(student_info_dict)
print(tags)


