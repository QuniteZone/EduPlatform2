### 用于存放数据库的表格类
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import func

db = SQLAlchemy()




class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Integer, nullable=False)  # 0:选择, 1:填空, 2:简答
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    status = db.Column(db.String(20), default='active')
    crt_ans = db.Column(db.Text, nullable=True)  # 存储参考答案的 JSON 字符串
    stu_ans = db.Column(db.Text, nullable=True)  #假象一个学生答案




class Answer_Log(db.Model):
    __tablename__ = 'answerlog'  # 定义表名
    id = db.Column(db.String(255), primary_key=True)  # 主键
    test_participate_id = db.Column(db.String(255), nullable=False)  # 参与ID
    user_id = db.Column(db.String(255), nullable=False)  # 用户ID
    test_paper_id = db.Column(db.String(255), nullable=False)  # 试卷ID
    session_id = db.Column(db.String(255), nullable=False)  # 会话ID
    section_id = db.Column(db.String(255), nullable=False)  # 章节ID
    section_item_id = db.Column(db.String(255), nullable=False)  # 章节项目ID
    question_id = db.Column(db.String(255), nullable=False)  # 问题ID
    question_bank_id = db.Column(db.String(255), nullable=False)  # 题库ID
    question_type = db.Column(db.String(255), nullable=False)  # 问题类型
    subjective_question_answer = db.Column(db.String(255), nullable=True)  # 主观题答案
    simple_question_answer = db.Column(db.String(255), nullable=True)  # 简单题答案
    total_score = db.Column(db.String(255), nullable=True)  # 总分
    score = db.Column(db.String(255), nullable=True)  # 得分
    item_status = db.Column(db.String(255), nullable=True)  # 项目状态
    review_result = db.Column(db.String(255), nullable=True)  # 审核结果
    review_type = db.Column(db.String(255), nullable=True)  # 审核类型
    review_user_id = db.Column(db.String(255), nullable=True)  # 审核用户ID
    org_id = db.Column(db.String(255), nullable=True)  # 组织ID
    create_by = db.Column(db.String(255), nullable=True)  # 创建人
    update_by = db.Column(db.String(255), nullable=True)  # 更新人
    create_time = db.Column(db.String(255), nullable=True)  # 创建时间
    update_time = db.Column(db.String(255), nullable=True)  # 更新时间
    deleted = db.Column(db.String(255), nullable=True)  # 删除标记
    tenant_id = db.Column(db.String(255), nullable=True)  # 租户ID


class CourseTask(db.Model):
    __tablename__ = 'course_task'  # 定义表名

    id = db.Column(db.String(255), primary_key=True)  # 主键
    course_id = db.Column(db.String(255), nullable=False)  # 课程ID
    plan_id = db.Column(db.String(255), nullable=False)  # 计划ID
    catalog_id = db.Column(db.String(255), nullable=False)  # 目录ID
    lesson_id = db.Column(db.String(255), nullable=False)  # 课程ID
    task_type = db.Column(db.String(255), nullable=False)  # 任务类型
    finish_condition_type = db.Column(db.String(255), nullable=True)  # 完成条件类型
    finish_condition = db.Column(db.String(255), nullable=True)  # 完成条件
    activity_attachment_id = db.Column(db.String(255), nullable=True)  # 活动附件ID
    file_length = db.Column(db.String(255), nullable=True)  # 文件长度
    file_name = db.Column(db.String(255), nullable=True)  # 文件名
    org_id = db.Column(db.String(255), nullable=True)  # 组织ID
    publish_status = db.Column(db.String(255), nullable=True)  # 发布状态
    sort_num = db.Column(db.String(255), nullable=True)  # 排序号
    create_by = db.Column(db.String(255), nullable=True)  # 创建人
    update_by = db.Column(db.String(255), nullable=True)  # 更新人
    create_time = db.Column(db.String(255), nullable=True)  # 创建时间
    update_time = db.Column(db.String(255), nullable=True)  # 更新时间
    deleted = db.Column(db.String(255), nullable=True)  # 删除标记
    tenant_id = db.Column(db.String(255), nullable=True)  # 租户ID


class Students(db.Model):
    __tablename__ = 'students'  # 定义表名称

    id = db.Column(db.String(50), primary_key=True)  # 主键
    student_id = db.Column(db.String(50), nullable=False)  # 学生ID
    org_id = db.Column(db.String(50), nullable=False)  # 组织ID
    org = db.Column(db.String(50), nullable=True)  # 组织
    disabled = db.Column(db.String(50), nullable=True)  # 禁用状态
    auth_code = db.Column(db.String(50), nullable=True)  # 授权码
    faculty = db.Column(db.String(50), nullable=True)  # 院系
    administrative_classes = db.Column(db.String(50), nullable=True)  # 行政班级
    major = db.Column(db.String(50), nullable=True)  # 专业
    deleted = db.Column(db.String(50), nullable=True)  # 删除标记


class Study_Task(db.Model):
    __tablename__ = 'study_task'  # 定义表名称

    id = db.Column(db.String(255), primary_key=True)  # 主键
    course_id = db.Column(db.String(255), nullable=False)  # 课程ID
    plan_id = db.Column(db.String(255), nullable=False)  # 计划ID
    catalog_id = db.Column(db.String(255), nullable=False)  # 目录ID
    lesson_id = db.Column(db.String(255), nullable=False)  # 课时ID
    task_type = db.Column(db.String(255), nullable=False)  # 任务类型
    title = db.Column(db.String(255), nullable=False)  # 标题
    finish_condition_type = db.Column(db.String(255), nullable=True)  # 完成条件类型
    finish_condition = db.Column(db.String(255), nullable=True)  # 完成条件
    activity_attachment_id = db.Column(db.String(255), nullable=True)  # 活动附件ID
    file_length = db.Column(db.String(255), nullable=True)  # 文件长度
    file_name = db.Column(db.String(255), nullable=True)  # 文件名
    org_id = db.Column(db.String(255), nullable=True)  # 组织ID
    publish_status = db.Column(db.String(255), nullable=True)  # 发布状态
    sort_num = db.Column(db.String(255), nullable=True)  # 排序号
    create_by = db.Column(db.String(255), nullable=True)  # 创建人
    update_by = db.Column(db.String(255), nullable=True)  # 更新人
    create_time = db.Column(db.String(255), nullable=True)  # 创建时间
    update_time = db.Column(db.String(255), nullable=True)  # 更新时间
    deleted = db.Column(db.String(255), nullable=True)  # 删除标记
    tenant_id = db.Column(db.String(255), nullable=True)  # 租户ID


class Studylog(db.Model):
    __tablename__ = 'studylog'  # 定义表名称

    id = db.Column(db.String(255), primary_key=True)  # 主键
    record_id = db.Column(db.String(255), nullable=False)  # 记录ID
    task_id = db.Column(db.String(255), nullable=False)  # 任务ID
    lesson_id = db.Column(db.String(255), nullable=False)  # 课时ID
    course_id = db.Column(db.String(255), nullable=False)  # 课程ID
    course_plan_id = db.Column(db.String(255), nullable=False)  # 课程计划ID
    study_time = db.Column(db.String(255), nullable=True)  # 学习时间
    status = db.Column(db.String(255), nullable=True)  # 状态
    classes_id = db.Column(db.String(255), nullable=True)  # 班级ID
    org_id = db.Column(db.String(255), nullable=True)  # 组织ID
    create_by = db.Column(db.String(255), nullable=True)  # 创建人
    update_by = db.Column(db.String(255), nullable=True)  # 更新人
    create_time = db.Column(db.String(255), nullable=True)  # 创建时间
    update_time = db.Column(db.String(255), nullable=True)  # 更新时间
    deleted = db.Column(db.String(255), nullable=True)  # 删除标记





