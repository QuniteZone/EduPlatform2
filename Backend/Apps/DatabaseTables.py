### 用于存放数据库的表格类
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import func

db = SQLAlchemy()

class User(db.Model):
    # 数据表明、字段
    __tablename__ = 'qgz_user'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    head = db.Column(db.String(100))
    nickName = db.Column(db.String(100))
    status = db.Column(db.Date)



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



class KnowledgePoint(db.Model):
    __tablename__ = 'knowledge_points'
    knowledge_ID = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Float, nullable=False) # 知识点权重


class Offline_Resource(db.Model):
    __tablename__ = 'offline_resources'  # 定义表名
    video_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 定义视频ID，为主键，自增
    title = db.Column(db.String(255), nullable=False)  # 定义标题，不能为空
    link = db.Column(db.String(255), nullable=False)  # 定义链接，不能为空
    upload_time = db.Column(db.DateTime, default=func.now())  # 定义上传时间，默认为当前时间
    duration = db.Column(db.String(20), nullable=False)  # 定义时长，不能为空
    views = db.Column(db.Integer, default=0)  # 定义观看次数，默认为0
    likes = db.Column(db.Integer, default=0)  # 定义点赞次数，默认为0
    favorites = db.Column(db.Integer, default=0)  # 定义收藏次数，默认为0
    shares = db.Column(db.Integer, default=0)  # 定义分享次数，默认为0
    tags = db.Column(db.JSON, nullable=True)  # 使用 JSON 类型，可以为空

