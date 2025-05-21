import uuid
from datetime import datetime
import os
import json
import pandas as pd
import numpy as np
import fitz  # PyMuPDF
import docx  # python-docx
from flask import Blueprint, jsonify, request
from .genericFunction import LLM, lesson_plan_prompt, class_meeting_prompt, allowed_file, extract_text_from_pdf, \
    extract_text_from_docx, ragflow, script_gen_prompt, jugement_ques_prompt, generate_question_prompt, \
    get_globalWeb_source,divide_learning_style,recommendation_prompt,student_knowledge
from config.config import TextbookRetr_AgentID, UPLOAD_FOLDER, LLMs_ALLOWED_FILE_EXTENSIONS,resourceFinder_AgentID

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
    print("教案提示词",promtp)
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
    print("教案提示词",promtp)
    messages = [{"role": "system",
                 "content": "你是一个班会稿生成专家，严格按Markdown格式((```markdown (生成的内容)```))输出结构化班会稿内容，确保键值命名与层级关系绝对准确"},
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
@lesson_plan_bp.route('/study_plan', methods=['GET','POST'])
def create_study_plan():
    stu_knowledge=student_knowledge() #获得学生的各个知识点掌握情况
    data = request.get_json()# 从请求中获取 JSON 数据

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


    #学习风格函数
    study_style=divide_learning_style()
    # print(f"study_style:{study_style}")

    # study_aim = "想一周之内，学习数字素养基础内容知识。例如编程基础、开源教育"
    study_aim =f"我的目标是{goal}，我打算每周学习{time}小时，我的学习背景是{background}，我的学习偏好是{preferences}，计划的开始时间：{current_time},截止日期是{deadline}。"

    result1, result2 = get_globalWeb_source(study_aim)
    onlineSearch = result2
    if result1 != None:
        onlineSearch = result1 + result2



    try:
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
    except Exception as e:
        print(f"An error occurred: {e}")
        source_response_data = None

    new_prompt = recommendation_prompt.format(study_aim=study_aim, student_type=study_style, knowledge_point=stu_knowledge,
                               source_response_data=source_response_data, onlineSearch=onlineSearch)

    messages = [
        {"role": "system",
         "content": "你是一个学习计划生成专家，严格按json格式((```json (生成的内容)```))输出结构化学习计划内容，确保键值命名与层级关系绝对准确"},
        {"role": "user", "content": new_prompt}]

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
                 "content": "你是一个资深教育工作者，按照用户提供信息来出题。严格按Markdown格式(```markdown (生成的内容)```)输出结构化教案内容，确保键值命名与层级关系绝对准确"},
                {"role": "user", "content": promtp}]

    return_result = LLM(messages, is_json=False)

    return jsonify({
        "content": return_result,
        "status": 1
    })



