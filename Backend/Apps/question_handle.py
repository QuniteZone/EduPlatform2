import json
import os
import uuid

import numpy as np
import requests
from openai import OpenAI
from flask import Blueprint, jsonify, request, stream_with_context, Response
from werkzeug.utils import secure_filename

from .genericFunction import LLMs_allowed_file, LLMs_StreamOutput, LLM, ragflow, get_globalWeb_source
from .config import LLMs_IMAGE_UPLOAD_FOLDER,LLMs_FILE_UPLOAD_FOLDER,Public_ip,LLMs_model

ques_handle_bp = Blueprint('ques_handle', __name__)




@ques_handle_bp.route('/get_LLM_key', methods=['GET'])
def get_LLM_key():
    key = os.environ["OPENAI_API_KEY"]
    print(f"key:{key}")
    return jsonify({"api_key": key})


#####多模态的问题问答
@ques_handle_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"content": "没有文件上传", 'status': 0})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"content": "没有选择文件", 'status': -1})

    # 确定文件类型并保存
    if file and LLMs_allowed_file(file.filename, 'image'):
        # 生成唯一的文件名
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path=f"{LLMs_FILE_UPLOAD_FOLDER}/{unique_filename}"
        file.save(file_path)
        fileIP=f"{Public_ip}/{file_path}"
        print(f"image fileIP:{fileIP}")
        return jsonify({"content": "图片上传成功", "fileIP": fileIP, 'status': 1})
    elif file and LLMs_allowed_file(file.filename, 'file'):
        # 生成唯一的文件名
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path = f"{LLMs_FILE_UPLOAD_FOLDER}/{unique_filename}"
        file.save(file_path)
        fileIP = Public_ip + file_path
        print(f"file fileIP:{fileIP}")
        return jsonify({"content": "文件上传成功", "fileIP": fileIP, 'status': 1})
    else:
        return jsonify({"content": "不支持的文件类型", 'status': -2})


@ques_handle_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    image_urls = data.get('image_urls')  # 从请求中获取图片URL，至少是一个空list
    # files_urls = data.get('files_urls')  # 从请求中获取文件的URL
    user_message = data.get('message')  # 从请求中获取用户消息及历史记录

    user_mesg = user_message[-1]['content']  # 获取最新一条的用户消息提问
    del user_message[-1]

    content_images = []  # 构建最新一条的user提问消息内容
    if image_urls != []:
        for image_url in image_urls:
            obj_img = {
                "type": "image_url",
                "image_url": {"url": image_url},
            }
            content_images.append(obj_img)
    content_images.append({"type": "text", "text": user_mesg})

    # 创建聊天完成请求
    messages=[]
    for message in user_message:
        if message['role']=="user":
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message['content'],
                    }
                ]
            })
        else:
            messages.append(message)


    messages.append({
        "role": "user",
        "content": content_images})

    print(f"最终message:{messages}")

    response = Response(stream_with_context(LLMs_StreamOutput(messages)), content_type='text/plain')

    return response





#  - 基于知识点集合总库，对题库题目利用LLM进行标注，构建题目知识点总库
@ques_handle_bp.route('/questionBank/Tagged', methods=['GET'])
def questionBankTagged():
    def process_questions(questions):
        prompt = ""
        for question in questions:
            prompt += f"题目ID：{question['ques_ID']}"
            if question["ques_type"] == "简答题":
                prompt += f"题目：{question['ques_Stem']} 请回答这个简答题。"
            elif question["ques_type"] == "选择题":
                prompt += f"题目：{question['ques_Stem']} 选项是：{question['ques_other']} 请从中选择一个正确的选项。"

            prompt += f" 答案是：{question['ques_answer']}."
            if question["ques_explanation"]:
                prompt += f" 解析：{question['ques_explanation']}"
            # 如果不是最后一个
            if question != questions[-1]:
                prompt += "；"

        return prompt

    def questionLLLM_Tagged(questions, knowledges_set):

        # 使用函数处理问题
        ques_output = process_questions(questions)  # 待解析的题目

        prompt = """
                一，任务描述：你需要对用户输入的题目进行知识点标注。请根据题目内容从知识点集合总库中提取相关的知识点，并将其以标准的JSON格式返回。
                对于解析题目知识点的表述，尽量从知识库中找到对应描述。若知识库中没有，则自行使用表述大众、规范统一的知识点描述。
                下面是知识库内容。
                {knowledges_set}        
                以上是知识库内容。

                二、输入的题目
                输入的题目是带有题目ID的形式，后续题目输出以ID作为标识符即可。
                {questions}

                三，输出格式
                输出格式需要严格按照如下格式来，仅需返回题目ID和接应解析知识点即可（尽量每道题目仅涉及一个知识点），且请确保你的输出能够被Python的json.loads函数解析，此外不要输出其他任何内容！
                ```json
                    {{
                        "knowledgeTag": [
                        {{
                            "ques_ID":1,
                            "knowledges":['加法'，'减法']
                        }},
                        {{
                            "ques_ID":2,
                            "knowledges":['加法'，'减法']
                        }}
                        ]
                    }}
                ```
              """
        prompt = prompt.format(knowledges_set=knowledges_set, questions=ques_output)

        messages = [{"role": "system",
                     "content": "你是一个资深的教育工作者，你需要分析用户给出题目中隐含的知识点"},
                    {"role": "user", "content": prompt}]

        message = LLM(messages)

        return message['knowledgeTag']

    knowledges_set = [ #模拟的知识点总库
        "基本代数运算",
        "三角函数",
        "概率与统计",
        "微积分基础",
        "线性方程组",
        "几何性质",
        "数列与极限",
        "数学建模"
    ]

    # questions中存储题目ID、题干、题目类型、题目答案、题目解析、其他内容
    questions = [ #模拟的存储的题库
        {
            "ques_ID": 1,
            "ques_Stem": "请解答以下方程：2x + 3 = 7。",
            "ques_type": "简答题",
            "ques_other": "",
            "ques_answer": "x = 2",
            "ques_explanation": "通过移项和除法运算可得x的值。"
        },
        {
            "ques_ID": 2,
            "ques_Stem": "在直角三角形中，已知一个锐角为30度，求另外一个锐角和斜边的关系。",
            "ques_type": "选择题",
            "ques_other": "A: 1/2  B: √3/2  C: 1/√2  D: 1",
            "ques_answer": "B",
            "ques_explanation": "根据三角函数关系，另一个锐角为60度，对应的正弦值为√3/2。"
        },
        {
            "ques_ID": 3,
            "ques_Stem": "随机投掷一枚硬币，求出现正面的概率。",
            "ques_type": "简答题",
            "ques_other": "",
            "ques_answer": "0.5",
            "ques_explanation": "因为正面和反面的可能性相等，产生正面的概率为1/2。"
        },
        {
            "ques_ID": 4,
            "ques_Stem": "计算定积分 ∫(0到1)(x^2)dx。",
            "ques_type": "简答题",
            "ques_other": "",
            "ques_answer": "1/3",
            "ques_explanation": "使用基本的积分计算法则，定积分得到的值为1/3。"
        },
        {
            "ques_ID": 5,
            "ques_Stem": "求解以下线性方程组：x + y = 5; 2x - y = 1。",
            "ques_type": "简答题",
            "ques_other": "",
            "ques_answer": "x = 2, y = 3",
            "ques_explanation": "通过代入法或消元法求解得出x和y的值。"
        }
    ]


    #每次模拟利用LLM解析2道题目
    for i in range(0,len(questions),2):
        question = questions[i:i+2]
        knowledgeTags=questionLLLM_Tagged(question, knowledges_set)
        # print(f"question:{question}")
        # print(f"knowledgeTags:{knowledgeTags}")
        for kt in knowledgeTags:
            print(f"ques_ID:{kt['ques_ID']},knowledges:{kt['knowledges']}")


    return "test"



#构造一个学习路径推荐的路由 学习路径——示例 /ques/recommend/learningPath
@ques_handle_bp.route('/recommend/learningPath', methods=['GET'])
def recommend_learningPath():


    need_study_knowledge=[
        {"knowledge_ID": 1, "content": "HTML基础语法", "weight": 0.55},
        {"knowledge_ID": 2, "content": "CSS基础语法", "weight": 0.54},
        {"knowledge_ID": 3, "content": "JavaScript基本语法", "weight": 0.56},
        {"knowledge_ID": 4, "content": "响应式设计原理", "weight": 0.50},
        {"knowledge_ID": 5, "content": "DOM操作与事件处理", "weight": 0.53},
        {"knowledge_ID": 6, "content": "CSS布局模型", "weight": 0.48},
        {"knowledge_ID": 7, "content": "CSS选择器的使用", "weight": 0.45},
        {"knowledge_ID": 8, "content": "JavaScript异步编程", "weight": 0.50},
        {"knowledge_ID": 9, "content": "Web标准与最佳实践", "weight": 0.40},
        {"knowledge_ID": 10, "content": "CSS预处理器（如Sass、Less）", "weight": 0.42},
        {"knowledge_ID": 11, "content": "JavaScript框架（如React、Vue）", "weight": 0.51},
        {"knowledge_ID": 12, "content": "前端构建工具（如Webpack）", "weight": 0.49},
        {"knowledge_ID": 13, "content": "版本控制工具（如Git）", "weight": 0.44},
        {"knowledge_ID": 14, "content": "表单验证与处理", "weight": 0.47},
        {"knowledge_ID": 15, "content": "API与前后端交互", "weight": 0.52},
        {"knowledge_ID": 16, "content": "浏览器开发者工具使用", "weight": 0.46},
        {"knowledge_ID": 17, "content": "CSS框架（如Bootstrap、Tailwind）", "weight": 0.55},
        {"knowledge_ID": 18, "content": "网页加载优化技巧", "weight": 0.48},
        {"knowledge_ID": 19, "content": "跨域问题及解决方案", "weight": 0.45},
        {"knowledge_ID": 20, "content": "JavaScript设计模式", "weight": 0.50},
        {"knowledge_ID": 21, "content": "图形与动画（如Canvas、SVG）", "weight": 0.41},
        {"knowledge_ID": 22, "content": "国际化与本地化", "weight": 0.39},
        {"knowledge_ID": 23, "content": "SEO基础知识", "weight": 0.37},
        {"knowledge_ID": 24, "content": "Web安全基础（如XSS、CSRF）", "weight": 0.54},
        {"knowledge_ID": 25, "content": "CSS变量与自定义属性", "weight": 0.43},
        {"knowledge_ID": 26, "content": "模块化JavaScript", "weight": 0.46},
        {"knowledge_ID": 27, "content": "前端性能监控", "weight": 0.38},
        {"knowledge_ID": 28, "content": "浏览器兼容性处理", "weight": 0.40},
        {"knowledge_ID": 29, "content": "Web组件概念", "weight": 0.33},
        {"knowledge_ID": 30, "content": "前端架构模式", "weight": 0.35},
        {"knowledge_ID": 31, "content": "单页应用（SPA）开发", "weight": 0.49},
        {"knowledge_ID": 32, "content": "多页面应用（MPA）开发", "weight": 0.45},
        {"knowledge_ID": 33, "content": "Websocket及实时通信", "weight": 0.43},
        {"knowledge_ID": 34, "content": "前端测试基础（如Jest）", "weight": 0.42},
        {"knowledge_ID": 35, "content": "类型检查与TypeScript", "weight": 0.41},
        {"knowledge_ID": 36, "content": "图形用户界面设计原则", "weight": 0.37},
        {"knowledge_ID": 37, "content": "UX/UI设计基础", "weight": 0.36},
        {"knowledge_ID": 38, "content": "移动端适配技巧", "weight": 0.39},
        {"knowledge_ID": 39, "content": "服务工作者与离线应用", "weight": 0.32},
        {"knowledge_ID": 40, "content": "CSS Grid布局", "weight": 0.48},
        {"knowledge_ID": 41, "content": "Flexbox布局", "weight": 0.44},
        {"knowledge_ID": 42, "content": "编写可访问性友好的网站", "weight": 0.46},
        {"knowledge_ID": 43, "content": "使用图标字体与SVG", "weight": 0.34},
        {"knowledge_ID": 44, "content": "前端部署与发布流程", "weight": 0.38},
        {"knowledge_ID": 45, "content": "Web前端框架选择", "weight": 0.35},
        {"knowledge_ID": 46, "content": "自定义事件与事件总线", "weight": 0.42},
        {"knowledge_ID": 47, "content": "Webpack配置与使用", "weight": 0.35},
        {"knowledge_ID": 48, "content": "代码优化与重构", "weight": 0.41},
        {"knowledge_ID": 49, "content": "小型与大型项目管理", "weight": 0.36},
        {"knowledge_ID": 50, "content": "邮件模板编写", "weight": 0.33},
        {"knowledge_ID": 51, "content": "动态数据绑定原理", "weight": 0.50},
        {"knowledge_ID": 52, "content": "客户端路由管理", "weight": 0.45},
        {"knowledge_ID": 53, "content": "环境变量与配置管理", "weight": 0.40},
        {"knowledge_ID": 54, "content": "前端代码规范与Lint工具", "weight": 0.39},
        {"knowledge_ID": 55, "content": "使用状态管理库（如Redux）", "weight": 0.52},
        {"knowledge_ID": 56, "content": "TypeScript在前端开发中的应用", "weight": 0.46},
        {"knowledge_ID": 57, "content": "使用图形库进行可视化（如D3.js）", "weight": 0.38},
        {"knowledge_ID": 58, "content": "UI组件库的使用与定制", "weight": 0.49},
        {"knowledge_ID": 59, "content": "异步请求的优化", "weight": 0.44},
        {"knowledge_ID": 60, "content": "客户端存储技术（如LocalStorage、SessionStorage）", "weight": 0.50},
        {"knowledge_ID": 61, "content": "使用微服务架构进行前端开发", "weight": 0.46},
        {"knowledge_ID": 62, "content": "使用RESTful API设计规范", "weight": 0.43},
        {"knowledge_ID": 63, "content": "使用GraphQL进行数据获取", "weight": 0.52},
        {"knowledge_ID": 64, "content": "日期与时间处理库（如Moment.js）", "weight": 0.37},
        {"knowledge_ID": 65, "content": "用户身份验证与授权", "weight": 0.55},
        {"knowledge_ID": 66, "content": "动态导入与代码分割", "weight": 0.40},
        {"knowledge_ID": 67, "content": "使用CSS动画增强用户体验", "weight": 0.35},
        {"knowledge_ID": 68, "content": "前端开发中的数据格式（如JSON、XML）", "weight": 0.43},
        {"knowledge_ID": 69, "content": "利用状态管理优化复杂应用", "weight": 0.48},
        {"knowledge_ID": 70, "content": "本地开发环境的搭建与使用", "weight": 0.36},
        {"knowledge_ID": 71, "content": "视频与音频处理", "weight": 0.30},
        {"knowledge_ID": 72, "content": "使用安全框架提高应用安全性", "weight": 0.45},
        {"knowledge_ID": 73, "content": "可重用组件的设计与架构", "weight": 0.42},
        {"knowledge_ID": 74, "content": "开发环境与生产环境的区别", "weight": 0.38},
        {"knowledge_ID": 75, "content": "网站性能分析工具的使用", "weight": 0.31},
        {"knowledge_ID": 76, "content": "使用客户反馈改善用户体验", "weight": 0.41},
        {"knowledge_ID": 77, "content": "文档编写与团队协作", "weight": 0.36},
        {"knowledge_ID": 78, "content": "使用配置文件管理项目设置", "weight": 0.34},
        {"knowledge_ID": 79, "content": "数据可视化的前端技术", "weight": 0.30},
        {"knowledge_ID": 80, "content": "访问性测试与审核", "weight": 0.32},
        {"knowledge_ID": 81, "content": "相关工具与技术栈的选择", "weight": 0.33},
        {"knowledge_ID": 82, "content": "自适应与响应式设计的区别", "weight": 0.35},
        {"knowledge_ID": 83, "content": "前端框架生态概述", "weight": 0.29},
        {"knowledge_ID": 84, "content": "搭建本地服务器进行调试", "weight": 0.30},
        {"knowledge_ID": 85, "content": "小型项目快速开发技巧", "weight": 0.36},
        {"knowledge_ID": 86, "content": "处理移动端特有的问题", "weight": 0.40},
        {"knowledge_ID": 87, "content": "和后端协作的有效沟通", "weight": 0.34},
        {"knowledge_ID": 88, "content": "数据流管理与优化", "weight": 0.35},
        {"knowledge_ID": 89, "content": "模块化CSS的实践", "weight": 0.32},
        {"knowledge_ID": 90, "content": "使用方言与框架的优缺点", "weight": 0.29},
        {"knowledge_ID": 91, "content": "了解Web Components的标准", "weight": 0.30},
        {"knowledge_ID": 92, "content": "编写文档与开发规范", "weight": 0.31},
        {"knowledge_ID": 93, "content": "图像优化与处理技术", "weight": 0.33},
        {"knowledge_ID": 94, "content": "动画与交互设计基础", "weight": 0.35},
        {"knowledge_ID": 95, "content": "使用第三方库与框架", "weight": 0.32},
        {"knowledge_ID": 96, "content": "微服务前端架构探讨", "weight": 0.28},
        {"knowledge_ID": 97, "content": "CMS的前端整合", "weight": 0.37},
        {"knowledge_ID": 98, "content": "客户端的性能考量", "weight": 0.39},
        {"knowledge_ID": 99, "content": "Web应用的法律合规", "weight": 0.30},
        {"knowledge_ID": 100, "content": "前端开发者与用户的支持技巧", "weight": 0.36}
    ]

    study_aim="想一周之内，学习数字素养基础内容知识。例如编程基础、开源教育"

    student_type="视觉型学习者"
    result1,result2=get_globalWeb_source(study_aim)
    onlineSearch=result2
    if result1!=None:
        onlineSearch=result1+result2

    # query = request.args.get('user')
    resourceFinder_AgentID="6c3e724a226611f08d100242ac120006"


    ###### RAGflow中检索资源库内容
    # 构建代理Agent会话
    agent_session_id = ragflow.create_agent_session(resourceFinder_AgentID)

    # 进行代理Agent聊天
    question = f"{study_aim}"

    source_response_data = ragflow.send_agent_message(resourceFinder_AgentID, question, stream=False,session_id=agent_session_id)

    # 删除该Agent会话
    ragflow.delete_agent_session(resourceFinder_AgentID, agent_session_id)
    ###### RAGflow中检索资源库内容

    prompt = """
一、任务描述：你需要根据用户输入的学习目标、学习风格和知识点要求，结合已有的推荐资源，制定一个清晰的学习路径。学习路径包括阶段规划和时间安排，同时清晰说明每个阶段的学习任务和目标。

二、用户输入
用户输入包括学习目标、学习风格、需要掌握的知识点和推荐资源，请根据这些要素制定学习路径。
学习目标：{study_aim}
学习风格：{student_type}
--------------------------
以下是知识点掌握情况，知识点的权值是指知识点掌握情况。取值为0-1，值越大掌握情况越好：
{knowledge_point}
以上是知识点掌握情况。
--------------------------
以下是从资源库中检索的资源情况（后面输出tasks的resources部分从该库中选择）：
{source_response_data}
以上是从资源库中检索的资源情况。
--------------------------
以下是网络相关资讯库，实时检索的博客视频等相关资讯（后面输出tasks的online_source部分从该库中选择）：
{onlineSearch}
以上是网络相关资讯库。

三、要求
1. 学习路径应包括多个阶段，每个阶段有明确的学习目标和时间安排，需要分析任务的难易，综合划分合理的不同阶段。总阶段数保持在2-10个左右。
2. 每个阶段应包含至少两个学习任务，每个任务应包括任务名称、任务描述、所需资源、在线资源等。
3. 学习路径应考虑到不同学习风格的需求，如视觉型学习者应优先考虑视频教程和图片资料等。
4. 学习路径应尽可能涵盖用户需要掌握的所有知识点，并确保每个知识点都有相应的学习任务。
5. 学习路径应提供实际可行的建议，帮助用户在实际操作中提升学习效果。
8. 学习路径应考虑到用户的实际需求，例如，如果用户要求规定在一周内完成任务，则整体任务必须规定在一周内。
9. 学习路径应尽可能提供多样化的学习资源，如在线课程、书籍、视频等。
10.从选用的任何online_source内容，都需要原内容输出。不允许修改、不允许遗漏。
11.输出tasks的resources部分和online_source部分不允许为空，其中online_source至少需要有三个。另外online_source至少需要选择两个视频。
12.video_summary只需要包含视频中简介内容，并且不允许缺失，需要提取关于视频简介的全部内容。其余内容无需提取。
13.提取的tags需要包含"tags"建的所有值，不允许遗漏，修改等操作。

四、输出格式
输出格式需遵循以下格式，确保信息清晰有序；同时请确保你的输出能被Python的json.loads函数解析，此外不要输出其他任何内容！
```json
{{
"learningPath": [
{{
"stage": "第一阶段",
"duration": "2025.4.26-2025.4.30",
"goal": "达到基础口语交流能力",

"suggestion": "在练习口语时，请确保发音准确，并注意语调的变化。同时，可以尝试与母语为英语的人进行交流，以提升实际应用能力。",
"tasks": [
    {{
        "taskName": "学习日常对话",
        "taskDescription": "学习日常对话，包括问候、介绍、询问天气等基本对话内容。",#尽量详细点，按照总分，通过xx达到xx目标等形式。
        "learningObjectives":["基本问候语（如你好、早上好）","自我介绍的常用句型","询问对方姓名的方式","询问天气的常用句子","日常生活中的常见对话场景（如购物、点餐）","基本感谢与道歉的表达方式","询问时间和日期的句型","描述天气状况的常用形容词（如晴天、雨天）","进行闲聊的常用话题（如兴趣爱好）","结束对话的礼貌用语"],#该任务涉及需要学习、强化的知识点。list对象呈现
        "resources": [
            {{   
                "title": "4月18日 如何准备2025年教师数字素养大赛？2",
                "link": "https://www.bilibili.com/video/BV1di4y1z7QM/",
                "preview_image_url": "https://i2.hdslb.com/bfs/archive/e5f442cb6b847082217ab7c557f296c81479836b.jpg@672w_378h_1c_!web-search-common-cover",
                "upload_time": "2024-01-07 09:28:01",
                "duration": "",
                "views": "1574",
                "likes": "15",
                "favorites": "33",
                "shares": "26",
                "tags": ["科普","数据","智慧","数字化转型","数字素养"], #不允许缺失项。需要包含所有原标签
                "video_summary": "什么是数字素养？\n\n数字素养是指个体对数字化环........."
            }},
            {{
                "title": "4月18日 如何准备2025年教师数字素养大赛？2",
                "link": "https://www.bilibili.com/video/BV1cA5Cz3ETc/",
                "preview_image_url": "https://i1.hdslb.com/bfs/archive/f2008926f0edd2759d655e1265f2e09a4998300a.jpg@672w_378h_1c_!web-search-common-cover",
                "upload_time": "2025-04-18 11:57:37",
                "duration": "",
                "views": "322",
                "likes": "2",
                "favorites": "17",
                "shares": "3",
                "tags": [ "教育","原创","大赛","学习","广东省教师数字素养提升实践大赛","老师"
                ],
                "video_summary": "视频信息\n·\n名称：4月18日 如何准......"
            }}],  # 请从资源库中检索资源，包括各种链接等。忠于“资源库中检索的资源情况”内容。
        "online_source": [
            {{
                "title": "B站最强学习资源汇总（数据科学，机器学习，Python） - 豫南- 博客园",
                "link": "https://www.cnblogs.com/lqshang/p/17281644.html",
                "introcude": "这门课程将学会理解业界构建深度神经网络应用最有效的做法； 能够高效地使用神经网络通用的技巧，包括初始化、L2和dropout正则化、Batch归一化、梯度检验",
                "is_video":0,
            }},
            {{
                "title": "机器学习技术与实现——MATLAB大数据处理- MATLAB",
                "link": "https://it.mathworks.com/videos/matlab-machine-learning-techniques-for-big-data-processing-100945.html",
                "introcude": "相关资源. 相关产品. MATLAB · 使用MATLAB 衔接无线通信设计与测试 · 阅读 ... 基础教学：符号. 58:23 视频长度为58:23 · MATLAB大学基础教学: 符号数学 ...",
                “times":"27:36",
                "update_time":"2022年7月31日",
                "image_url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRcUtGr9vKE1cCl4s5m7p4dYjqChUyl7o6LlDtsO9GeOCTa&s",
                "is_video":1,
            }},
            {{
                "title": "机器学习技术与实现——MATLAB大数据处理- MATLAB",
                "link": "https://it.mathworks.com/videos/matlab-machine-learning-techniques-for-big-data-processing-100945.html",
                "introcude": "相关资源. 相关产品. MATLAB · 使用MATLAB 衔接无线通信设计与测试 · 阅读 ... 基础教学：符号. 58:23 视频长度为58:23 · MATLAB大学基础教学: 符号数学 ...",
                “times":"27:36",
                "update_time":"2022年7月31日",
                "image_url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRcUtGr9vKE1cCl4s5m7p4dYjqChUyl7o6LlDtsO9GeOCTa&s",
                "is_video":1,
            }},
        ] #请从网络检索工具中检索资源，包括各种链接等。忠于“网络相关资讯库”内容。
    }},
    {{
        "taskName": "练习发音技巧",
        "taskDescription": "练习发音技巧，包括音标、连读、重音等。",
        "resources": ......,
        "online_source": ......
    }}
]
}},
{{
"stage": "第二阶段",
"duration": "2025.5.1-2025.5.7",
"goal": "达到流利口语交流能力",
"suggestion": "在练习口语时，请确保发音准确，并注意语调的变化。同时，可以尝试与母语为英语的人进行交流，以提升实际应用能力。",
"tasks": [
    {{
        "taskName": "参与讨论活动",
        "taskDescription": "通过讨论活动提高口语流利度。",
        "resources": ......,
        "online_source": ......
    }},
    {{
        "taskName": "加强听力练习",
        "taskDescription": "通过听新闻、播客等素材来提升听力理解能力。",
        "resources": ......,
        "online_source": ......
    }}
]
}}
],
"suggestion": [
"在练习口语时，请确保发音准确，并注意语调的变化。同时，可以尝试与母语为英语的人进行交流，以提升实际应用能力。",
"建议每日练习与模拟对话，设定每日的口语练习时间，比如30分钟，进行英语口语的自我练习。这可以包括朗读课文、跟读英语视频或音频，或与语言交换伙伴进行对话练习",
"观看和模仿英语影视作品,选择一些您喜欢的英语电影、电视剧或YouTube频道，观看时注意人物的对话和语音语调。暂停并模仿他们的发音和表达方式。"
] #请根据学生的学习进度和表现，给出个性化的3-5条学习建议。
}}
```
"""

    new_prompt = prompt.format(study_aim=study_aim, student_type=student_type, knowledge_point=need_study_knowledge, source_response_data=source_response_data, onlineSearch=onlineSearch)

    messages = [{"role": "user", "content": new_prompt}]

    print("*"*50)
    #json缩进形式打印message
    print(f"new_prompt:{new_prompt}")

    print("*" * 50)


    message = LLM(messages)

    print("*"*50)
    #json缩进形式打印message
    print(json.dumps(message, indent=4, ensure_ascii=False))

    print("*" * 50)

    return "test"
#