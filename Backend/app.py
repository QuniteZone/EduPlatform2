from flask import Flask
from flask_cors import CORS
from Apps.lesson_plan import lesson_plan_bp
from Apps.question_handle import ques_handle_bp
from Apps.DatabaseTables import db
import config.config
from config.config import Config

app = Flask(__name__)
# 注册蓝图
app.register_blueprint(lesson_plan_bp, url_prefix='/plan')  # 可以设置 URL 前缀
app.register_blueprint(ques_handle_bp, url_prefix='/ques')  # 可以设置 URL 前缀
CORS(app)

config_obj = Config()
app.config.from_object(config.config)
app.config.from_object(config_obj)
db.init_app(app) # 初始化数据库


# 获取服务配置
service_config = config_obj.SERVICE_CONFIG
# 自动注册到 Nacos 微服务
if service_config.enable_nacos:
    service_config.connect()  # 自动注册服务到 Nacos
    print(f"Service {service_config.instance_name} registered to Nacos")


@app.route('/')
def home():
    return "successful！这里是EduPlatform系统！"


if __name__ == '__main__':
    with app.app_context():  # 进入应用上下文
        db.create_all()  # 创建表格
    # app.run(host='0.0.0.0', port=service_config.current_service_port)
    app.run(host='0.0.0.0', port=service_config.current_service_port, debug=True)
    # app.run(host='127.0.0.1',port=service_config.current_service_port, debug=True)
    # app.run(port=service_config.current_service_port, debug=True)