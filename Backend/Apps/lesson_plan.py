import io
import time
from datetime import datetime

from flask import Blueprint, jsonify, request
from .genericFunction import LLM,lesson_plan_prompt,class_meeting_prompt,allowed_file,extract_text_from_pdf,extract_text_from_docx,ragflow,script_gen_prompt,jugement_ques_prompt,generate_question_prompt
from .config import TextbookRetr_AgentID,QuesGen_AgentID

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
def get_lesson_plan2():
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


#这是依据教案生成逐字稿的过程
@lesson_plan_bp.route('/lesson_script', methods=['POST'])
def handle_lesson_script():
    try:
        require = request.form.get('requires') #
        uploaded_files = request.files.getlist('files')
        parsed_texts = {}
        content = {}  # 返回结构
        content["status"] = 1
        content["content"] = None
        updata_text=""
        if not uploaded_files:
            content["status"] = -1  # 表示文件未上传
            return jsonify(content)
        import PyPDF2
        import docx
        from docx import Document
        if not uploaded_files:
            content["status"] = -1  # 表示文件未上传
            return jsonify(content)

        for uploaded_file in uploaded_files:
            print(f"上传的文件名: {uploaded_file.filename}")  # 打印文件名
            print(f"文件大小: {uploaded_file.content_length} bytes")  # 打印文件大小

            # 检查文件大小
            if uploaded_file.content_length == 0:
                content['status'] = -2
                content['message'] = f"{uploaded_file.filename} 文件为空"
                return jsonify(content)
            # 根据文件类型处理文件
            if uploaded_file.filename.endswith('.docx'):
                document = Document(uploaded_file.stream)  # 用流方式读取文件内容
                full_text = []
                for para in document.paragraphs:
                    full_text.append(para.text)
                document_content = '\n'.join(full_text)
                print("Word 内容:", document_content)
                content["content"] = document_content

        print(f"require:{require}")
        print(f"updata_text:{updata_text}")

        # if parsed_text=="":
        #     pass
            #不执行RAGflow端

        #下面代码是好的。不改变

        # ##将从知识库中检索内容，然后作为输入一并给到LLM进行处理。
        # # 构建代理Agent会话
        # lesson_plan= """
        # 教学设计方案：
        # 一、课程标准
        # •	教学主题：素质基础素养
        # •	适用情境：面向大一年级的素质素养课堂，适用于初学阶段，帮助学生理解素质素养的核心概念及其在生活中的应用
        # •	教学内容：包括素质素养的基本概念、重要性以及在学习和生活中的实际应用，引导学生将理论与实践结合
        # •	教学目标：
        # 输入本节课希望学生达到的预期学习成果，包括知识、能力、情感等方面
        # •	课时安排：2课时（约90分钟）
        # 二、教学设计
        # 1. 新课导入
        # •	教学程序： 教师提问：“大家觉得在大学生活中，哪些素质是最重要的？为什么？” 播放一段关于素质素养的重要性的视频，激发学生的兴趣 引导学生分享他们的看法，形成对素质素养的初步理解
        # •	设计意图： “通过引导学生思考与生活中相关的现象或问题来激发兴趣，使他们感知到素质素养的实际意义，建立对新课的认同感和学习动力。”
        # 2. 自主学习
        # •	教学程序： 学生通过课本和网络资源，进行自主学习，深入理解素质素养的相关内容 学生思考并记录重要问题，如： 素质素养的定义是什么？ 它如何在实际中得到应用？ 学生认为掌握这一知识的意义何在？
        # •	设计意图： “培养学生独立获取知识的能力，并通过思考和探讨帮助他们形成对素质素养的深入理解，激励学生的探究精神。”
        # 3. 案例分析
        # •	教学程序： 教师提供相关案例（如：“在职场中，如何运用素质素养来提升个人竞争力？”），并引导学生分析 学生小组合作讨论，解决实际问题后进行汇报，并与全班分享思路和结果
        # •	设计意图： “通过具体案例让学生看到素质素养的实际应用，增强学生的分析与解决问题的能力，同时在小组合作中锻炼团队协作与交流能力。”
        # 4. 学习评价
        # •	教学程序： 教师通过思维导图或小测验等方式帮助学生回顾学习内容 学生进行自评和互评，总结自己的收获并对学习过程进行反思，教师给予反馈
        # •	设计意图： “帮助学生回顾所学内容，评估他们对素质素养的掌握程度，激励他们进行自我反思，促进更深层次的知识内化。”
        # ________________________________________
        # 5. 小结
        # •	教学程序： 教师总结本课的关键知识点，并引导学生讨论如何将这些知识应用到其他学科或实际问题中 提出开放性问题，如：“如何将今天学到的素质素养知识应用到未来的职业生涯中？”
        # •	设计意图： “巩固课堂所学的知识，并帮助学生将知识系统化，培养他们将学到的知识运用于其他领域的能力。”
        # 6. 作业布置
        # •	教学程序： 任务一：完成与本课相关的练习或思考题 任务二：选择一个实际案例，分析素质素养在其中的应用，并准备报告或展示材料
        # •	设计意图： “通过课后任务强化学生对素质素养的理解与应用，激发他们的独立思考和分析能力，同时为学生提供实践的机会。”
        # ________________________________________
        # 三、素养目标
        # •	学科素养：理解并掌握素质素养的核心概念，能够在实际问题中进行有效应用
        # •	技术与应用能力：能够将所学知识运用于具体问题的解决中，进行分析与方案设计
        # •	创新与批判性思维：能够从多角度分析问题，提出独立且创新的解决方案
        # •	合作与表达：能够在小组合作中有效沟通、清晰表达个人观点并进行反馈交流
        # """ #这是教案
        # agent_session_id = ragflow.create_agent_session(TextbookRetr_AgentID)
        #
        # # 进行代理Agent聊天
        # response_data = ragflow.send_agent_message(TextbookRetr_AgentID, lesson_plan, stream=False, session_id=agent_session_id)
        #
        # # 删除该Agent会话
        # ragflow.delete_agent_session(TextbookRetr_AgentID,agent_session_id)
        #
        # question = f"要求给我生成一份大概在40分钟左右的逐字稿，要是需是田老师作为老师回复"
        #
        # promtp = script_gen_prompt.format(teachPlan=lesson_plan, textbook=response_data, require=question)
        # messages = [{"role": "system",
        #              "content": "你是一名专业教育工作者，有多年教学经验。"},
        #             {"role": "user", "content": promtp}]
        # return_result = LLM(messages,False)
        #
        # ## 调用LLM实现逐字稿返回
        # if response_data==None and parsed_text == None:
        #     content["status"]=-2  #系统报错，出现文件或知识库检索为空
        #     content["content"] = None
        #     return jsonify(content)
        #
        #
        # content["content"] = return_result
        # return jsonify(content)

        return "test 中"
    except Exception as e:
        content["status"] = 0 #报错
        content["content"] = e
        return jsonify(content)



##仅作为一个测试示例
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
    content["status"] = 1
    content["content"] = "None  联系qgz"










    return jsonify(content)



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



