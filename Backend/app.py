import json
import os

from flask import Flask, jsonify
from flask_cors import CORS
# 导入蓝图
from Apps.lesson_plan import lesson_plan_bp
from Apps.question_handle import ques_handle_bp
from Apps.DatabaseTables import db, User, Question, KnowledgePoint, Offline_Resource
import config.config

app = Flask(__name__)
# 注册蓝图
app.register_blueprint(lesson_plan_bp, url_prefix='/plan')  # 可以设置 URL 前缀
app.register_blueprint(ques_handle_bp, url_prefix='/ques')  # 可以设置 URL 前缀
CORS(app)

app.config.from_object(config.config)
db.init_app(app)

@app.route('/')
def home():
    return "你好，这里是EduPlatform系统！"


if __name__ == '__main__':
    with app.app_context():  # 进入应用上下文
        db.create_all()  # 创建表格
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=5001, debug=True)
    # app.run(host='127.0.0.1',port=5001, debug=True)
    # app.run(port=5001, debug=True)