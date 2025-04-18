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