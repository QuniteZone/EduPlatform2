import uuid
from datetime import datetime
import os
import json
import random

import pandas as pd
import numpy as np
import fitz  # PyMuPDF
import docx  # python-docx
from flask import Blueprint, jsonify, request
from .genericFunction import LLM, get_user_profile, StudentClusterModel, student_knowledge
from config.config import TextbookRetr_AgentID, UPLOAD_FOLDER, LLMs_ALLOWED_FILE_EXTENSIONS,resourceFinder_AgentID
from datetime import timedelta
import ast
from .DatabaseTables import db, Answer_Log, CourseTask, Students, Study_Task, Studylog

from sqlalchemy import func,text

#这是教案生成
user_plan_bp = Blueprint('user_plan', __name__)


#课程数据呈现页面
@user_plan_bp.route('/course_data', methods=['GET', 'POST'])
def get_course_data():

    # 统计学生数
    student_count = Students.query.filter_by().count()  # 这里假定 deleted 用于标记已删除的记录
    # 获取班级数，假设班级信息在 `administrative_classes` 列中
    class_count = Students.query.filter_by().with_entities(func.count(Students.administrative_classes.distinct())).scalar()
    study_count = Studylog.query.filter_by().count()  #统计 总的学习次数
    # 统计学习时长的总和
    total_study_time = Studylog.query.with_entities(func.sum(Studylog.study_time)).scalar() or 0

    # 人均学习时长
    avg_study_time = total_study_time / student_count if student_count > 0 else 0
    per_capita_study_time = round(avg_study_time, 2)  # 保留两位小数

    # 人均学习次数
    avg_study_count = study_count / student_count if student_count > 0 else 0
    per_capita_study_count = round(avg_study_count, 2)  # 保留两位小数




    ### 获取学习最新的学习动态
    #获取学生的日志行为
    study_logs = (
        Studylog.query
        .outerjoin(Study_Task, Studylog.lesson_id == Study_Task.lesson_id)
        .filter()
        .with_entities(Studylog, Study_Task.title)
        .order_by(Studylog.update_time.desc())
        .limit(50)
        .all()
    )
    logList = [] #学生学习日志
    if study_logs:
        for log,title in study_logs:
            update_time = datetime.strptime(log.update_time, '%Y-%m-%d %H:%M:%S')
            logList.append({
                'stu': str(log.create_by)[-4:],
                'time':  update_time.strftime('%Y-%m-%d %H:%M') if update_time else None,
                'chapter': f"数字素养-{eval(title)}",
                "times": log.study_time or 0,
            })


    # print(f"学生学习日志：\n{logList}")

    ## 学生近一周访问次数情况
    StudentTime = Studylog.query.with_entities(
        func.date(Studylog.update_time).label('day'),
        func.count().label('record_count')
    ).group_by(
        func.date(Studylog.update_time)
    ).order_by(
        text('day DESC')
    ).limit(7).all()
    latest_7_LogResult = [
        row.record_count  for row in StudentTime
    ]


    ## 学生的专业分布情况统计
    major_distribution = (
        Students.query
        .with_entities(Students.major, func.count(Students.id).label('count'))
        .group_by(Students.major)
        .order_by(func.count(Students.id).desc())
        .limit(10)
        .all()
    )
    major_list=[]# 转换为列表，方便前端展示
    for major, count in major_distribution:
        major_list.append(
            {'value': count, 'name': major}
        )  #专业表
    # print(f"学生的专业分布情况统计：\n{major_list}\n{major_count}")


    ## 课程任务类型 考察方式 情况统计
    # 统计任务类型分布，按数量降序
    task_type_distribution = (
        CourseTask.query
        .with_entities(CourseTask.task_type, func.count(CourseTask.id).label('count'))
        .group_by(CourseTask.task_type)
        .order_by(func.count(CourseTask.id).desc())
        .all()
    )
    task_type_list = []  # 转换为列表，方便前端展示
    task_type_dict={
        '0':"图文",
        '1':"视频",
        '2':"音频",
        '3':"讨论",
        '4':"文档",
        '5':"PPT",
        '9':"其他",
    }
    for task_type, count in task_type_distribution:
        task_type_list.append(
            {'name': task_type_dict[task_type], 'value': count},
        )  #任务类型表
    # print(f"课程任务类型 考察方式 情况统计：\n{task_type_list}\n{task_count_list}")


    needData = {
        # 数字指标卡片
        'studentCount': student_count,
        'classCount': class_count,
        # 图谱路径
        'knowledgeGraphUrl': '/All_shuzi_Xiaorong.json',
        # 学习相关指标
        'learningCount': f'{round(study_count/10000,0)}万次', #学习总次数
        'learningDuration': f'{round(total_study_time/3600/10000 ,2)}万h', #学习总时长
        'avgLearningFrequency': f'{per_capita_study_count}次',  # 人均学习次数
        'avgLearningDuration': f"{round(per_capita_study_time/3600,2)}h", # 人均学习时长

        # 折线图：近一周学习情况
        'weeklyLearningTrend': {
            'title': '数字素养',
            'categories': ['周一', '周二', '周三', '周四', '周五', '周六','周日'],
            'seriesData': [
                {'name': '学习人次', 'data': latest_7_LogResult},
            ],
        },
        # 考察情况分布
        'pie1Data': {
            'title': '',
            'seriesData': task_type_list,     # 课程任务资源类型 分布表
            'legend': True
        },
        'pie2Data': {
            'title': '学生专业分布',
            'subtext': '专业分布',
            'seriesName': 'Access From',
            'radius': '50%',
            'seriesData': major_list   #课程学生 专业分布表
        },
        # 表格数据 - 排行榜
        'topClassProgress': logList  #最新课程学生学习日志
    }

    # print(f"最终数据整合：\n{needData}")
    #

    return jsonify(needData),200



#用户画像个人数据呈现页面
@user_plan_bp.route('/Tags', methods=['GET', 'POST'])
def get_tags():
    def convert_numbers_to_labels(numbers):
        number_to_label_map = {
            0: "沉浸式学习者",
            1: "稳健型学习者",
            2: "随性式学习者",
            3: "刷题型学习者",
            4: "节奏型学习者",
            5: "轻量型学习者",
            6: "任务终结者",
            7: "稳定跟进者",
            8: "起步困难户",
            9: "深度沉浸者",
            10: "节奏掌控者",
            11: "碎片化学习者",
            12: "白昼学习者",
            13: "夜间学习者",
            14: "弹性时间派",
            15: "视听偏好者",
            16: "文本偏好者",
            17: "动手实践者",
            18: "混合型学习者",
            19: "全能探索者",
            20: "专注深耕者",
            21: "专一执行者"
        }

        return [number_to_label_map[number] for number in numbers]

    def process_knowledge_points(data, seed=None):
        # 按照权重（第二个元素）进行降序排序
        sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

        # 设置随机种子
        if seed is not None:
            random.seed(seed)

        # 随机抽取前半部分和后半部分的知识点
        top_half = sorted_data[:100]
        bottom_half = sorted_data[100:]

        top_8 = random.sample(top_half, 8)
        bottom_8 = random.sample(bottom_half, 8)

        return {
            'top_8': [(point[0], point[1]) for point in sorted(top_8, key=lambda x: x[1], reverse=True)],
            'bottom_8': [(point[0], point[1]) for point in sorted(bottom_8, key=lambda x: x[1])]
        }

    # 输出需要查询的学生ID 和起始的时间
    # student_id = "1830475870539571200"
    data_time = '2024-10-11 00:00:00'  # current time 起始时间
    student_id =request.json.get('student_id')

    #获取统计分析学生基本信息
    data,tags=get_user_profile(student_id,data_time)
    StrTags=convert_numbers_to_labels(tags)
    # print(f"data:\n {data}, \ntags: {tags}")
    # print(f"StrTags:{StrTags}")

    cluster_labels = {
        0: '自主领袖型',
        1: '自主管理型',
        2: '被动接受型',
        3: '反复试探型',
        4: '目标模糊型',
        5: '随机应变型',
        6: '静默观察型'
    }
    loaded_model = StudentClusterModel.load_model()  # 加载模型
    cluster = loaded_model.predict(student_id, data_time)
    student_ml_lable=cluster_labels.get(cluster, '未知类型')
    StrTags.append(student_ml_lable)


    #分析学生知识点掌握情况
    stu_knowledge = student_knowledge()  # 获得学生的各个知识点掌握情况
    result = process_knowledge_points(stu_knowledge, student_id)
    top_points, top_scores = zip(*result['top_8'])
    top_points_list,top_scores_list=list(top_points),list(top_scores) #top 知识点 得分
    bottom_points, bottom_scores = zip(*result['bottom_8'])
    bottom_points_list,bottom_scores_list=list(bottom_points),list(bottom_scores) #bottom 知识点 得分

    #获取学生的日志行为
    study_logs = (
        Studylog.query
        .outerjoin(Study_Task, Studylog.lesson_id == Study_Task.lesson_id)
        .filter(Studylog.create_by == student_id)
        .with_entities(Studylog, Study_Task.title)
        .order_by(Studylog.update_time.desc())
        .all()
    )
    logList = [] #学生学习日志
    if study_logs:
        for log,title in study_logs:
            update_time = datetime.strptime(log.update_time, '%Y-%m-%d %H:%M:%S')
            if log.study_time !=0 and log.study_time !="0" and title != "课程PPT" and title !="\"课程PPT\"" :
                logList.append({
                    "data": update_time.strftime('%Y-%m-%d') if update_time else None,
                    "time": update_time.strftime('%H:%M') if update_time else None,
                    "lesson": "数字素养",
                    "teach": eval(title) or "未知课程",
                    "times": round(float(log.study_time)/60,2) or 0,
                })

    # 利用LLM生成学习建议
    prompt_plan=f"""请你根据下面的信息，给出这位学生一些学习建议。
        学生基本信息：
            班级：{data["class"]}
            学校：{data["school"]}
            专业：{data["major"]}
        学生标签：
            {StrTags}
        学生知识点掌握情况：
            最好的8个知识点：{top_points_list}
            最好的8个知识点分数：{top_scores_list}
            最差的8个知识点：{bottom_points_list}
            最差的8个知识点分数：{bottom_scores_list}
        学生学习日志：
            {logList}
        学生总答题数：{data["answer_count"]}
        学生总学习时间：{data["total_study_time"]}
        学生正确答题数：{data["correct_rate"]}
    
    二、学习建议的输出参考格式
    请直接回复一个json字符串对象，不要有其他多于内容。输出格式需要严格按照如下格式来，且请确保你的输出能够被Python的json.loads函数解析，此外不要输出其他任何内容！
        ```json
            {{
                "suggest": [
                    "利用下午（占比 50% ）高效时段，多攻克复杂知识，比如深入钻研前端框架难点，匹配高活跃状态。",
                    "总做题量 5 道不算多，可增加题量巩固知识，同时结合 0.8 的正确率，分析错题类型，针对性提升。",
                    "学习风格里 “独立” 维度突出，遇到难题先自主思考；“交流” 维度稍弱，可多参与学习讨论，互补提升。",
                ]
            }}
        ```

    """
    messages = [{"role": "system",
                 "content": "对学生基本情况分析，然后给出学习建议！"},
                {"role": "user", "content": prompt_plan}]
    return_result=LLM(messages)
    print(f'时间：{round(data["total_study_time"]/60)}')

    json_data = {
        "data": {
            "stu_data": {
                # 基本信息
                "name": "None",
                "id": student_id,
                "class": data["class"],
                "school": data["school"],
                "major": data["major"],

                # 四个小卡片
                "all_questions": data["answer_count"],
                "all_lessons": 1,
                "all_time": round(data["total_study_time"]/60),
                "right": data["correct_rate"],

                # 最好的8知识点和其分数
                "top_points_list":top_points_list,
                "top_scores_list": top_scores_list,

                # 最差的8知识点和其分数
                "bottom_points_list": bottom_points_list,
                "bottom_scores_list": bottom_scores_list,

                # 学习记录
                "info": logList,

                # 学习建议 可支持多条
                "goals": return_result['suggest'],

                # 风格标签
                "styles": StrTags,
            }
        }
    }

    # print(f"用户画像前端返回数据：\n{json_data}")
    # 返回标签列表
    return jsonify(json_data), 200