import io
import time
import uuid
from datetime import datetime
import os
import json
import fitz  # PyMuPDF
import docx  # python-docx

from flask import Blueprint, jsonify, request
from .genericFunction import LLM, lesson_plan_prompt, class_meeting_prompt, allowed_file, extract_text_from_pdf, \
    extract_text_from_docx, ragflow, script_gen_prompt, jugement_ques_prompt, generate_question_prompt, \
    get_globalWeb_source
from .config import TextbookRetr_AgentID, QuesGen_AgentID, UPLOAD_FOLDER, LLMs_ALLOWED_FILE_EXTENSIONS

#这是教案生成
lesson_plan_bp = Blueprint('lesson_plan', __name__)

#自动生成教案
@lesson_plan_bp.route('/lesson_plan', methods=['GET', 'POST'])
def get_lesson_plan():
    if request.method == 'POST':
        grade=request.json.get('grade')
        subject = request.json.get('subject')
        knowledge=request.json.get('knowledge')
    else:
        grade = request.args.get('grade')
        subject = request.args.get('subject')
        knowledge = request.args.get('knowledge')
    promtp=lesson_plan_prompt.format(grade=grade, subject=subject, knowledge=knowledge)
    messages = [{"role": "system",
                 "content": "你是一个教案生成专家，严格按Markdown格式输出结构化教案内容，确保键值命名与层级关系绝对准确"},
                {"role": "user", "content": promtp}]

    return_result=LLM(messages,is_json=False)
    content={} #返回结构
    if return_result==False:
        content["status"]=0 #报错
        content["content"]=None
    else:
        content["status"]=1
        content["content"]=return_result
    return_result=jsonify(content)
    return return_result


#自动生成班会稿
@lesson_plan_bp.route('/class_meeting', methods=['GET', 'POST'])
def class_meeting():
    if request.method == 'POST':
        grade=request.json.get('grade')
        knowledge=request.json.get('knowledge')
    else:
        grade = request.args.get('grade')
        knowledge = request.args.get('knowledge')
    promtp=class_meeting_prompt.format(grade=grade, knowledge=knowledge)
    messages = [{"role": "system",
                 "content": "你是一个班会稿生成专家，严格按Markdown格式输出结构化班会稿内容，确保键值命名与层级关系绝对准确"},
                {"role": "user", "content": promtp}]

    return_result=LLM(messages,is_json=False)
    content={} #返回结构
    if return_result==False:
        content["status"]=0 #报错
        content["content"]=None
    else:
        content["status"]=1
        content["content"]=return_result
    return_result=jsonify(content)
    return return_result


@lesson_plan_bp.route('/lesson_upload', methods=['POST'])
def lesson_upload():
    if 'file' not in request.files:
        return jsonify({"content": "没有文件上传", 'status': 0})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"content": "没有选择文件", 'status': -1})
    # 生成唯一文件名
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[-1]

    # 直接使用 UPLOAD_FOLDER 保存文件
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    return jsonify({"content": "文件上传成功", "status": 1, "filename": unique_filename})



#这是依据教案生成逐字稿的过程
@lesson_plan_bp.route('/lesson_script', methods=['POST'])
def handle_lesson_script():
    require = request.form.get('requires')
    uploaded_files = request.files.getlist('files')
    parsed_text=""

    if not uploaded_files:
        return jsonify({'error': '未收到任何文件'}), 400

    for file in uploaded_files:
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename=file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # # 解析文本内容
            # ext = filename.rsplit('.', 1)[1].lower()
            # if ext == 'pdf':
            #     parsed_text = extract_text_from_pdf(save_path)
            # elif ext == 'docx':
            #     parsed_text = extract_text_from_docx(save_path)
            # else:
            #     parsed_text = None

            # 解析文本内容
            split_filename = filename.rsplit('.', 1)
            if len(split_filename) > 1:
                ext = split_filename[1].lower()
                if ext == 'pdf':
                    parsed_text = extract_text_from_pdf(save_path)
                elif ext == 'docx':
                    parsed_text = extract_text_from_docx(save_path)
                else:
                    parsed_text = None
            else:
                # 处理没有扩展名的情况
                parsed_text = None  # 或者定义其他处理方法
        else:
            return jsonify({'error': f'不支持的文件类型: {file.filename}'}), 400

    con={}
    ##将从知识库中检索内容，然后作为输入一并给到LLM进行处理。
    # 构建代理Agent会话
    lesson_plan= parsed_text #这是教案
    agent_session_id = ragflow.create_agent_session(TextbookRetr_AgentID)

    # 进行代理Agent聊天
    response_data = ragflow.send_agent_message(TextbookRetr_AgentID, lesson_plan, stream=False, session_id=agent_session_id)

    # 删除该Agent会话
    ragflow.delete_agent_session(TextbookRetr_AgentID,agent_session_id)

    promtp = script_gen_prompt.format(teachPlan=lesson_plan, textbook=response_data, require=require)
    messages = [{"role": "system",
                 "content": "你是一名专业教育工作者，有多年教学经验。"},
                {"role": "user", "content": promtp}]
    return_result = LLM(messages,False)

    ## 调用LLM实现逐字稿返回
    if response_data==None:
        con["status"]=-2  #系统报错，出现文件或知识库检索为空
        con["content"] = None
        return jsonify(con)

    print(f"提示词：{promtp}\n####")

    con["content"] = return_result
    return jsonify(con)







##个性化学习 推荐
@lesson_plan_bp.route('/study_plan', methods=['POST'])
def create_study_plan():

    data = request.get_json()# 从请求中获取 JSON 数据
    content={} #返回内容

    # 检查必需的参数是否存在
    required_fields = ['goal', 'background', 'preferences', 'time', 'deadline', 'title']
    for field in required_fields:
        if field not in data:
            return jsonify({'content': f'缺少参数: {field}','status':0})

    # 提取参数
    goal = data['goal']
    background = data['background']
    preferences = data['preferences']
    time = data['time']
    deadline = data['deadline']
    title = data['title']

    # 在这里可以添加处理学习计划的逻辑
    # 例如，保存到数据库或进行其他处理
    # 这里我们只是返回接收到的数据作为示例
    #统计时间，返回当前时间
    now = datetime.now()

    # 格式化时间为字符串
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    content={
        'createdAt': current_time,
        'goal':goal,
        'background':background,
        'time':time,
        'deadline':deadline,
        'title':title,
    }

    need_study_knowledge = [
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

    study_aim = "想一周之内，学习数字素养基础内容知识。例如编程基础、开源教育"

    student_type = "视觉型学习者"
    result1, result2 = get_globalWeb_source(study_aim)
    onlineSearch = result2
    if result1 != None:
        onlineSearch = result1 + result2

    # query = request.args.get('user')
    resourceFinder_AgentID = "6c3e724a226611f08d100242ac120006"

    ###### RAGflow中检索资源库内容
    # 构建代理Agent会话
    agent_session_id = ragflow.create_agent_session(resourceFinder_AgentID)

    # 进行代理Agent聊天
    question = f"{study_aim}"

    source_response_data = ragflow.send_agent_message(resourceFinder_AgentID, question, stream=False,
                                                      session_id=agent_session_id)

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

    new_prompt = prompt.format(study_aim=study_aim, student_type=student_type, knowledge_point=need_study_knowledge,
                               source_response_data=source_response_data, onlineSearch=onlineSearch)

    messages = [{"role": "user", "content": new_prompt}]

    print("*" * 50)
    # json缩进形式打印message
    print(f"new_prompt:{new_prompt}")

    print("*" * 50)

    message = LLM(messages)

    print("*" * 50)
    # json缩进形式打印message
    print(json.dumps(message, indent=4, ensure_ascii=False))
    print("*" * 50)

    return jsonify({"content": message, 'status': 1})









# 主观题判题 question_judgment   http://192.168.31.172:5001/plan/question_judgment
@lesson_plan_bp.route('/question_judgment', methods=['POST'])
def question_judgment():
    data = request.get_json()# 从请求中获取 JSON 数据

    # 检查必需的参数是否存在
    required_fields = ['question', 'stu_ans']
    for field in required_fields:
        if field not in data:
            return jsonify({'content': f'缺少参数: {field}', 'status': 0})

    question = data.get('question')
    crt_ans = """"数字素养是指个人在数字环境中获取、评估、使用和创造信息的能力。它对现代人至关重要，主要体现在以下几个方面：1. 信息获取与筛选能力（3分）：在互联网时代，信息海量且复杂。数字素养能够帮助人们快速获取有价值的信息并筛选出虚假或误导性信息。例如，通过学习如何识别新闻来源的可靠性，避免传播未经证实的消息。2. 数据安全与隐私保护（3分）：数字素养包括了解如何保护个人数据和隐私。例如，使用强密码、定期更新软件以防止恶意软件攻击，以及避免在不安全的网络环境中输入敏感信息。3. 数字工具的应用能力（2分）：掌握基本的数字工具（如办公软件、在线协作平台等）能够提高工作效率。例如，利用云存储和在线办公软件进行远程协作，提升工作和学习的灵活性。4. 数字内容创作与传播（2分）：数字素养还涉及如何创作和传播高质量的数字内容。例如，通过学习基本的视频剪辑或图文编辑技能，能够更好地表达自己的观点并分享给他人。给分点： 每个要点根据阐述的完整性和举例的合理性进行评分，总分10分。""" #'crt_ans' 从数据库获取
    stu_ans = data.get('stu_ans')

    promtp = jugement_ques_prompt.format(question=question, crt_ans=crt_ans, stu_ans=stu_ans)
    messages = [{"role": "system",
                 "content": "你是一名阅卷老师，负责对学生的答案进行打分和评价"},
                {"role": "user", "content": promtp}]

    return_result = LLM(messages)

    content = {
        'content': return_result,
        'status': 1}
    return jsonify(content)





@lesson_plan_bp.route('/question_generate', methods=['POST'])
def question_generate():
    data = request.get_json()  # 从请求中获取 JSON 数据

    # 检查必需的参数是否存在
    required_fields = [
        'subject', 'grade',
        'questionType', 'difficulty', 'questionCount',
        'knowledgePoints', 'otherRequirements'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "content": f"缺少参数: {field}",
                "status": 0
            })

    # 提取参数
    subject = data['subject']
    grade = data['grade']
    question_type = data['questionType']
    difficulty = data['difficulty']
    question_count = data['questionCount']
    knowledge_points = data['knowledgePoints']
    other_requirements = data['otherRequirements']


    knowledges = f"""这是{subject}学科，{grade}年级，知识点：{knowledge_points}，从教材中检索返回知识点"""  # 这是教案
    agent_session_id = ragflow.create_agent_session(TextbookRetr_AgentID)
    # 进行代理Agent聊天
    response_data = ragflow.send_agent_message(TextbookRetr_AgentID, knowledges, stream=False,
                                               session_id=agent_session_id)
    # 删除该Agent会话
    ragflow.delete_agent_session(TextbookRetr_AgentID, agent_session_id)


    promtp = generate_question_prompt.format(subject=subject,grade=grade,  question_type=question_type,difficulty=difficulty,question_count=question_count,knowledges=knowledges,other_requirements=other_requirements,knowledge_points=knowledge_points)
    messages = [{"role": "system",
                 "content": "你是一个资深教育工作者，按照用户提供信息来出题。严格按Markdown格式输出结构化教案内容，确保键值命名与层级关系绝对准确"},
                {"role": "user", "content": promtp}]

    return_result = LLM(messages, is_json=False)

    return jsonify({
        "content": return_result,
        "status": 1
    })



