## 该文件用于存储后端所需基本配置信息
from nacos_service.nacos_utils import ServiceConfig
import json
import os


###################################### 动态参数变量配置 ######################################
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = ''
PORT = ''
DATABASE = ''
SQLALCHEMY_DATABASE_URI = f"{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True


#LLM 基本配置信息
os.environ["OPENAI_BASE_URL"] = ""
os.environ["OPENAI_API_KEY"] = ""
model = "gpt-4o-mini"
temperature=0.5 #LLM 温度


#多模态LLM的基本配置信息 QVQ -max
os.environ["DASHSCOPE_API_KEY"] = ""
LLMs_model="qvq-max"

Public_ip="" #后端公网IP地址


#rag_flow 基本配置信息
ragflow_BASE_URL = ""  # rag_flow的后端地址
ragflow_API_KEY = ""  # rag_flow的后端端口


TextbookRetr_AgentID = f"" #RAGflow中从知识库中检索教材知识点的AgentID
resourceFinder_AgentID = "" #RAGflow中从知识库中检索相关资源的AgentID


#网络检索的基本配置信息
web_video_url = ""
web_message_url=""
web_api_key=""



###################################### 固定参数变量配置 ######################################
#文件上传保存路径
# 配置上传文件的目录
LLMs_IMAGE_UPLOAD_FOLDER = 'static/LLM/images'  # 图片上传路径
LLMs_FILE_UPLOAD_FOLDER = 'static/LLM/files'      # 其他文件上传路径
UPLOAD_FOLDER = os.path.join('static', "uploads") #普通上传文件路径
os.makedirs(LLMs_IMAGE_UPLOAD_FOLDER, exist_ok=True)# 创建上传目录（如果不存在）
os.makedirs(LLMs_FILE_UPLOAD_FOLDER, exist_ok=True)
LLMs_ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的图片文件类型
LLMs_ALLOWED_FILE_EXTENSIONS = {'pdf', 'doc', 'docx'}          # 允许的文件类型


#后端注册为微服务——配置文件
class Config(object):
    __SVC_CONFIG_FP__ = None

    @property
    def SVC_CONFIG_FP(self):
        if self.__SVC_CONFIG_FP__ is None:
            self.__SVC_CONFIG_FP__ = os.path.join(os.path.dirname(__file__), "service.config")
        return self.__SVC_CONFIG_FP__

    @SVC_CONFIG_FP.setter
    def SVC_CONFIG_FP(self, fp):
        self.__SVC_CONFIG_FP__ = fp
        self.__SERVICE_CONFIG__ = ServiceConfig(config_fp=fp)

    # ** 只读属性 **
    __SERVICE_CONFIG__ = None

    @property
    def SERVICE_CONFIG(self):
        if self.__SERVICE_CONFIG__ is None:
            self.__SERVICE_CONFIG__ = ServiceConfig(config_fp=self.SVC_CONFIG_FP)
        return self.__SERVICE_CONFIG__