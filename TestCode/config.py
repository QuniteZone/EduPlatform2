## 该文件用于存储后端所需基本配置信息
import json
import os


DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'eduplatform'

#mysql 不会认识utf-8,而需要直接写成utf8
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True


#LLM 基本配置信息
# os.environ["OPENAI_BASE_URL"] = "https://api.chatanywhere.tech/v1"
# os.environ["OPENAI_API_KEY"] = "sk-OyEPaIflRbJXIospoq197kPskfatY1UmbfKKOszLJicK7RuJ"
# model = "gpt-4o-mini"
os.environ["OPENAI_BASE_URL"] = "https://api.chatanywhere.tech"
os.environ["OPENAI_API_KEY"] = "sk-QBFgXmIcXeaR5v40BZN3jabFKtSkoudkpIz4vmGU6V8Uu4N6"
model='gpt-3.5-turbo'
temperature=0.5 #LLM 温度


#rag_flow 基本配置信息
ragflow_BASE_URL = "http://127.0.0.1"  # rag_flow的后端地址
# ragflow_API_KEY = "ragflow-QwMDMzYWMyMTgzMzExZjBhZGI0MDI0Mm"  # rag_flow的 API Key
ragflow_API_KEY="ragflow-NhN2I5ODZhMTg0MzExZjA4OThkNWFiZW" #qgz 的api key密钥