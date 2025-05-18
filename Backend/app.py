from flask import Flask,request,g
from flask_cors import CORS
import logging
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
logging.basicConfig(level=logging.INFO) #配置日志

# 获取服务配置
service_config = config_obj.SERVICE_CONFIG
# 自动注册到 Nacos 微服务
if service_config.enable_nacos:
    service_config.connect()  # 自动注册服务到 Nacos
    print(f"Service {service_config.instance_name} registered to Nacos")


@app.before_request
def log_request():
    # 将 IP 地址和请求信息存储在全局变量 g 中
    g.start_time = request.start_time = None  # 如果需要记录请求开始时间，可以相应地初始化
    g.remote_ip = request.remote_addr
    g.method = request.method
    g.path = request.path


@app.after_request
def log_response(response):
    # 记录请求信息和响应状态码
    app.logger.info(
        "Request: %s %s | IP: %s | Status: %d",
        g.path,
        g.method,
        g.remote_ip,
        response.status_code
    )
    return response

@app.route('/')
def home():
    return "successful！这里是EduPlatform系统！"


if __name__ == '__main__':
    with app.app_context():  # 进入应用上下文
        db.create_all()  # 创建表格
    app.run(host='0.0.0.0', port=service_config.current_service_port, debug=True)