import os
import uuid
from flask import Blueprint, jsonify, request, stream_with_context, Response
from .genericFunction import LLMs_allowed_file, LLMs_StreamOutput, LLM, ragflow, get_globalWeb_source,LLM_StreamOutput
from config.config import LLMs_IMAGE_UPLOAD_FOLDER,LLMs_FILE_UPLOAD_FOLDER,Public_ip,LLMs_model

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


#知识点梳理——思维导图
@ques_handle_bp.route('/kn_chat', methods=['POST'])
def kn_chat():
    import time
    data = request.json
    user_message = data.get('message')  # 从请求中获取用户消息及历史记录
    title = data.get('title')  # 从请求中获取用户消息及历史记录

    user_mesg = user_message[-1]['content']  # 获取最新一条的用户消息提问

    print(f"最新一条的用户消息提问:{user_mesg}")
    print(f"最新一条的用户消息提问:{title}")

    messages = [
        {
            "role": "system",
            "content":"""你是一个思维导图专家，请根据用户输入的标题和内容生成思维导图，也就是返回markown格式内容，此外不要输出任何多余无关内容话语，例如如果用户提问，输出机器学习基础内容知识点，你需要回复下面内容：
            
# 机器学习基础知识点梳理
## 1. 机器学习概述
- 1.1 机器学习定义
- 1.2 机器学习与人工智能的关系
- 1.3 机器学习的分类
  - 1.3.1 监督学习
  - 1.3.2 无监督学习
  - 1.3.3 强化学习
            """
        },
        {
            "role": "user",
            "content": "机器学习基础内容知识点"
        }
    ]

    # return Response(stream_with_context(LLM_StreamOutput(messages)), content_type='text/plain')

    def generate_stream():
        # 模拟延迟的生成器
        messages = [
    "# 数字素养基础内容知识点梳理",
    "## 1. 数字素养的定义",
    "- 1.1 数字素养的概念",
    "- 1.2 数字素养的重要性",
    "- 1.3 数字素养的核心要素",
    "## 2. 数字工具与技术",
    "- 2.1 常用数字工具",
    "- 2.1.1 文档编辑工具",
    "- 2.1.2 表格处理工具",
    "- 2.1.3 演示文稿制作工具",
    "- 2.2 社交媒体的使用",
    "- 2.3 信息检索与评价",
    "## 3. 数据素养",
    "- 3.1 数据的收集与存储",
    "- 3.2 数据分析基础",
    "- 3.3 数据可视化技巧",
    "- 3.4 数据安全与隐私保护",
    "## 4. 数字沟通",
    "- 4.1 数字沟通的渠道",
    "- 4.2 高效的在线协作",
    "- 4.3 整合多种沟通工具",
    "- 4.4 电子邮件礼仪",
    "## 5. 数字公民身份",
    "- 5.1 网络礼仪与行为规范",
    "- 5.2 数字权益与责任",
    "- 5.3 网络安全意识",
    "- 5.4 防止虚假信息与网络欺诈",
    "## 6. 数字素养的应用",
    "- 6.1 教育中的数字素养",
    "- 6.2 工作场所中的数字素养",
    "- 6.3 生活中的数字素养",
    "- 6.4 持续学习与技能提升",
]
        # 逐条发送消息，模拟延迟
        for message in messages:
            yield f"data: {message}\n"
            # time.sleep(0.1)  # 模拟处理时间

    return Response(generate_stream(), content_type='text/event-stream')


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