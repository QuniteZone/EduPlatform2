## 该文件用于存储后端所需基本配置信息
import json
import os
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
#远程连接qgz的MySQL数据库 94686t61i9.zicp.fun:53604
# HOST = '94686t61i9.zicp.fun'
# PORT = '53604'
DATABASE = 'eduplatform'
#mysql 不会认识utf-8,而需要直接写成utf8
# SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
SQLALCHEMY_DATABASE_URI = f"{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True


#LLM 基本配置信息
os.environ["OPENAI_BASE_URL"] = "https://api.chatanywhere.org/v1"

os.environ["OPENAI_API_KEY"] = "sk-FUFiwSHFPr9S3ofp9kGjV17GoHYS3o1Ie3ekXwmsQgUaJO5i"
model = "gpt-4o-mini"
# os.environ["OPENAI_BASE_URL"] = "https://maas-api.cn-huabei-1.xf-yun.com/v1"
# os.environ["OPENAI_API_KEY"] = "sk-kWw6gDp0ZYWcNTMtD35a4f613921425a9c87312c36C5D3Ca"
# model='xdeepseekv3'
temperature=0.5 #LLM 温度


#多模态LLM的基本配置信息 QVQ -max
os.environ["DASHSCOPE_API_KEY"] = "sk-b8ee8eb0b16a4f8099a7492bdbe405c9"
LLMs_model="qvq-max"

#文件上传保存路径
# 配置上传文件的目录
LLMs_IMAGE_UPLOAD_FOLDER = 'static/LLM/images'  # 图片上传路径
LLMs_FILE_UPLOAD_FOLDER = 'static/LLM/files'      # 其他文件上传路径
os.makedirs(LLMs_IMAGE_UPLOAD_FOLDER, exist_ok=True)# 创建上传目录（如果不存在）
os.makedirs(LLMs_FILE_UPLOAD_FOLDER, exist_ok=True)
LLMs_ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的图片文件类型
LLMs_ALLOWED_FILE_EXTENSIONS = {'pdf', 'doc', 'docx'}          # 允许的文件类型
Public_ip="https://fz68ok24676.vicp.fun" #后端公网IP地址



#rag_flow 基本配置信息
# ragflow_BASE_URL = "http://127.0.0.1"  # rag_flow的后端地址
# https://9vh4ik686619.vicp.fun

ragflow_BASE_URL = "https://9vh4ik686619.vicp.fun"  # rag_flow的后端地址
# ragflow_API_KEY = "ragflow-QwMDMzYWMyMTgzMzExZjBhZGI0MDI0Mm"  # rag_flow的 API Key
ragflow_API_KEY = "ragflow-k5MTJmNmQ0MDdiMjExZjA5ZWY4MDI0Mm"  # rag_flow的后端端口


TextbookRetr_AgentID = f"4962e4b8240511f0bfb80242ac120006" #RAGflow中从知识库中检索教材知识点的AgentID
QuesGen_AgentID="cca846541d1d11f09a85ba9f4c68f6ef"


#网络检索的基本配置信息
web_video_url = "https://google.serper.dev/videos"
web_message_url="https://google.serper.dev/search"
web_api_key="54933bde17093ecd3db9ef1d25f16be7c3a5a6d2"



