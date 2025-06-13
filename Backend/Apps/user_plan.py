import uuid
from datetime import datetime
import os
import json
import pandas as pd
import numpy as np
import fitz  # PyMuPDF
import docx  # python-docx
from flask import Blueprint, jsonify, request
from .genericFunction import LLM
from config.config import TextbookRetr_AgentID, UPLOAD_FOLDER, LLMs_ALLOWED_FILE_EXTENSIONS,resourceFinder_AgentID
from datetime import timedelta
import ast
from .DatabaseTables import db, User, Answer_Log, CourseTask, Students, Study_Task, Studylog

#这是教案生成
user_plan_bp = Blueprint('user_plan', __name__)


@user_plan_bp.route('/Tags', methods=['GET'])
def get_user():
    # 查询学生基础信息
    def get_student_info(student_id):
        studentData = Students.query.filter_by(student_id=student_id).first()
        if studentData:
            faculty = studentData.faculty  # 学院
            class_name = studentData.administrative_classes  # 班级
            major = studentData.major  # 专业
        else:
            faculty = None
            class_name = None
            major = None
            print(f"没有找到学生信息")
        return faculty, class_name, major

    # 答题数据统计
    def get_answer_stats(student_id, current_date):
        AnswerLogData = Answer_Log.query.filter_by(user_id=student_id).all()
        if AnswerLogData:
            data = [{
                'user_id': log.user_id,
                'score': log.score,
                'review_result': log.review_result,
                'create_time': log.create_time
            } for log in AnswerLogData]

            df = pd.DataFrame(data)

            # 数据处理
            df['create_time'] = pd.to_datetime(df['create_time'])
            df['review_result'] = pd.to_numeric(df['review_result'], errors='coerce').fillna(0).astype(int)
            # 计算统计指标
            answer_count = len(df)
            correct_count = (df['review_result'] == 1).sum()
            correct_rate = correct_count / answer_count if answer_count > 0 else 0
            last_active = df['create_time'].max()
            # 计算最近7天答题数
            current_date = pd.to_datetime(current_date)
            start_date = current_date - timedelta(days=7)
            last_7_days_count = df[(df['create_time'] > start_date) & (df['create_time'] <= current_date)].shape[0]
            # 构建结果字典
            answerLogResutl = {
                'answer_count': answer_count,
                'correct_rate': correct_rate,
                'last_active': last_active,
                'last_7_days_answer_count': last_7_days_count
            }
        else:
            answerLogResutl = {}
            print(f"没有找到该学生的学习记录")
        return answerLogResutl

    # 学习数据统计
    def get_study_stats(student_id):
        study_logs = Studylog.query.filter_by(create_by=student_id).all()
        # 存储结果的列表
        StudyLogresults = []
        for log in study_logs:
            # 获取该学习日志对应的任务类型
            task_types = (Study_Task.query
                          .filter_by(lesson_id=log.lesson_id)
                          .with_entities(Study_Task.task_type)
                          .distinct()
                          .all()
                          )
            # 将任务类型转换为逗号分隔的字符串
            task_type_str = ','.join([task[0] for task in task_types]) if task_types else ''

            # 构建结果字典
            newStudyLog = {
                'lesson_id': log.lesson_id,
                'study_time': log.study_time,
                'status': log.status,
                'create_by': log.create_by,
                'create_time': log.create_time,
                'task_types': task_type_str
            }

            StudyLogresults.append(newStudyLog)
        StudyLogresultsData = pd.DataFrame(StudyLogresults)
        if StudyLogresultsData.empty:
            print(f"该学生没有学习记录")
            answerResult = {}
        else:
            # 数据处理
            StudyLogresultsData["study_time"] = pd.to_numeric(StudyLogresultsData["study_time"],
                                                              errors="coerce").fillna(0)
            StudyLogresultsData["status"] = pd.to_numeric(StudyLogresultsData["status"], errors="coerce").fillna(
                0).astype(int)
            StudyLogresultsData["create_time"] = pd.to_datetime(StudyLogresultsData["create_time"], errors="coerce")
            StudyLogresultsData["hour"] = StudyLogresultsData["create_time"].dt.hour
            total_study_time = StudyLogresultsData["study_time"].sum() / 60
            avg_study_time = StudyLogresultsData["study_time"].mean() / 60
            completed_df = StudyLogresultsData[StudyLogresultsData["status"] == 1]
            completed_tasks = len(completed_df)
            completion_rate = completed_tasks / len(StudyLogresultsData) if len(StudyLogresultsData) else 0

            def split_task_types(series):
                all_types = []
                for val in series.dropna():
                    all_types.extend(val.split(','))
                return all_types

            completed_task_types = split_task_types(completed_df["task_types"])
            task_type_count = len(set(completed_task_types))
            task_type_ratio = pd.Series(completed_task_types).value_counts(normalize=True).sort_index().round(
                3).to_dict()
            time_8_18 = StudyLogresultsData[(StudyLogresultsData["hour"] >= 8) & (StudyLogresultsData["hour"] < 18)][
                "study_time"].sum()
            time_18_24 = StudyLogresultsData[(StudyLogresultsData["hour"] >= 18) & (StudyLogresultsData["hour"] < 24)][
                "study_time"].sum()
            total_time_window = time_8_18 + time_18_24
            time_ratio = {
                "8-18": round(time_8_18 / total_time_window, 3) if total_time_window else 0,
                "18-24": round(time_18_24 / total_time_window, 3) if total_time_window else 0
            }
            answerResult = {
                "user_id": student_id,
                "total_study_time": round(total_study_time, 2),
                "avg_study_time": round(avg_study_time, 2),
                "completed_task_count": completed_tasks,
                "task_type_count": task_type_count,
                "task_type_ratio": task_type_ratio,
                "completion_rate": round(completion_rate, 2),
                "study_time_ratio": time_ratio
            }
        return answerResult
        pass

    #打标签
    def generate_student_tags(data):
        tags = []

        # 单位转换：秒转分钟
        total_study_time_min = data['total_study_time'] / 60
        avg_study_time_min = data['avg_study_time'] / 60

        recent_answer_count = data['last_7_days_answer_count']
        task_completion_rate = data['completion_rate']

        # task_type_ratio 和 study_time_ratio 可能是字符串，转换为字典
        task_type_ratio = ast.literal_eval(data['task_type_ratio']) if isinstance(data['task_type_ratio'], str) else \
        data['task_type_ratio']
        time_ratio = ast.literal_eval(data['study_time_ratio']) if isinstance(data['study_time_ratio'], str) else data[
            'study_time_ratio']

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

    #输出需要查询的学生ID 和起始的时间
    student_id="1842595446920237056"
    data_time='2024-10-11 00:00:00'  # current time 起始时间

    ##获取学生的信息 ##
    faculty, class_name, major= get_student_info(student_id)
    #获取学生的答题answerLog记录
    answerLogResutl = get_answer_stats(student_id, data_time)
    ###答题数据统计  #######  #并没有构建study_recore_task_test表，分别查询Studylog和Study_Task组合构建
    answerResult = get_study_stats(student_id)

    ###### 组合学生画像
    data = {
        "user_id": student_id,
        "faculty": faculty,
        "major": major,
        "class": class_name
    }
    if answerLogResutl:
        data.update({
            "answer_count": answerLogResutl["answer_count"],
            "correct_rate": round(answerLogResutl["correct_rate"], 3),
            "last_active": answerLogResutl["last_active"],
            "last_7_days_answer_count": answerLogResutl["last_7_days_answer_count"]
        })
    else:
        data.update({
            "answer_count": 0,
            "correct_rate": 0,
            "last_active": None,
            "last_7_days_answer_count": 0
        })

    if isinstance(answerResult, dict):
        data.update(answerResult)
    else:
        data["study_stats"] = answerResult


    #### 对数据进行打标签处理 ####
    TagResults=generate_student_tags(data)

    print(f"最终数据整合：\n{data}")
    print(f"最后标签结果为：")
    print(TagResults)

    return "e"