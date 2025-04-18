from datetime import datetime

from flask import Blueprint, jsonify, request
from .genericFunction import LLM,lesson_plan_prompt,allowed_file,extract_text_from_pdf,extract_text_from_docx,ragflow,script_gen_prompt,jugement_ques_prompt
from .config import TextbookRetr_AgentID

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


#这是依据教案生成逐字稿的过程
@lesson_plan_bp.route('/lesson_script', methods=['POST'])
def handle_lesson_script():
    try:
        require = request.form.get('require') #
        uploaded_files = request.files.getlist('files')
        parsed_texts = {}
        content = {}  # 返回结构
        content["status"] = 1
        content["content"] = None
        updata_text=""
        if not uploaded_files:
            content["status"] = -1  # 表示文件未上传
            return jsonify(content)
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()  # 直接读取文件内容
                if ext == 'pdf':
                    parsed_text = extract_text_from_pdf(file.stream)  # 使用 file.stream 直接读取
                else:
                    parsed_text = extract_text_from_docx(file.stream)  # 使用 file.stream 直接读取
                parsed_texts[file.filename] = parsed_text
                updata_text+=f"{file.filename}:{parsed_text}\n"
            else:
                content["status"] = -2  # 不支持该文件类型
                return jsonify(content)
                break
        ##将从知识库中检索内容，然后作为输入一并给到LLM进行处理。
        # 构建代理Agent会话
        important_para = {
            "lesson_plan": updata_text,
        }
        agent_session_id = ragflow.create_agent_session(TextbookRetr_AgentID,important_para=important_para)

        # 进行代理Agent聊天
        question = f"给我生成一份逐字稿，另外{require}"
        response_data = ragflow.send_agent_message(TextbookRetr_AgentID, question, stream=False, session_id=agent_session_id)

        # 删除该Agent会话
        ragflow.delete_agent_session(TextbookRetr_AgentID,agent_session_id)

        ## 调用LLM实现逐字稿返回
        if response_data==None and parsed_text == None:
            content["status"]=-2  #系统报错，出现文件或知识库检索为空
            content["content"] = None
            return jsonify(content)

        content["content"] = response_data
        return jsonify(content)
    except Exception as e:
        content["status"] = 0 #报错
        content["content"] = e
        return jsonify(content)






##仅作为一个测试示例
@lesson_plan_bp.route("/gen_question", methods=["POST"])
def get_info():
    data = request.get_json()# 从请求中获取 JSON 数据

    # 检查必需的参数是否存在
    required_fields = ['subject', 'grade', 'textbook', 'topic', 'questionType', 'difficulty', 'questionCount',
                       'knowledgePoints', 'otherRequirements']
    for field in required_fields:
        if field not in data:
            return jsonify({
        "content": None,
        "status": 0  #缺少参数
    })

    # 提取参数
    subject = data['subject']  #学科
    grade = data['grade']  #年级
    textbook = data['textbook']  #教材名称
    topic = data['topic']  #主题
    question_type = data['questionType']  #题型
    difficulty = data['difficulty']  #难度
    question_count = data['questionCount']  #问题数量
    knowledge_points = data['knowledgePoints']   #知识点
    other_requirements = data['otherRequirements']   #其他要求

    return jsonify({
        "content": "智能出题测试示例",
        "status": 1
    })


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
    content["content"] = """# 学习计划 - 计划A

## 学习目标
这是我的学习目标：**掌握机器学习的基本概念和应用**。

## 现有背景
这是我的现有背景：
- 具备基本的编程能力，熟悉 Python 语言。
- 了解数据分析的基础知识，使用过 Pandas 和 NumPy。
- 有一定的数学基础，熟悉线性代数和概率论。

## 学习偏好
我期望的学习资源方式：
- **文章/博客**：
  - [机器学习入门（Google Developers）](https://developers.google.com/machine-learning/crash-course)
  - [机器学习基础（Towards Data Science）](https://towardsdatascience.com/machine-learning-for-beginners-d47c2e4e6f5f)
  - [深度学习与机器学习的区别（Medium）](https://medium.com/@mohit.kumar/deep-learning-vs-machine-learning-7b9b8c8f2c7e)
  
- **项目**：
  - [Kaggle 机器学习项目](https://www.kaggle.com/learn/overview) - Kaggle 提供了许多机器学习项目和数据集，适合实践。
  - [机器学习项目示例（GitHub）](https://github.com/trekhleb/homemade-machine-learning) - 自制机器学习项目的示例代码。

- **视频**：
  - [Coursera 机器学习课程（Andrew Ng）](https://www.coursera.org/learn/machine-learning) - 由斯坦福大学的 Andrew Ng 教授讲授的经典课程。
  - [YouTube 机器学习基础视频](https://www.youtube.com/watch?v=Gv9_4yM6D3I) - 机器学习基础知识的快速入门视频。

## 每周学习时间
计划每周花费的学习时间：**12小时**。

## 截止日期
学习目标截止日期：**2025年04月18日 18:00**。

## 学习计划安排
### 第1周
- **目标**：了解机器学习的基本概念。
- **内容**：
  - 阅读机器学习入门文章（3小时）。
  - 观看机器学习基础视频（3小时）。
- **项目**：完成一个简单的线性回归项目（6小时）。

### 第2周
- **目标**：掌握监督学习和非监督学习的基本算法。
- **内容**：
  - 阅读关于监督学习和非监督学习的博客（3小时）。
  - 观看相关的在线课程（3小时）。
- **项目**：实现一个分类算法（如决策树）并进行实验（6小时）。

### 第3周
- **目标**：深入学习模型评估和选择。
- **内容**：
  - 阅读模型评估的相关文献（3小时）。
  - 观看模型选择的讲座（3小时）。
- **项目**：使用交叉验证评估模型性能（6小时）。

### 第4周
- **目标**：学习深度学习的基础知识。
- **内容**：
  - 阅读深度学习入门书籍的相关章节（3小时）。
  - 观看深度学习的在线课程（3小时）。
- **项目**：实现一个简单的神经网络（6小时）。

## 其他要求
- 每周总结学习内容，记录学习心得。
- 定期与学习小组讨论，分享学习进展和遇到的问题。

---

**备注**：请根据个人情况和学习进度调整学习计划，确保能够按时完成学习目标。
"""

    return jsonify(content)



# 主观题判题 question_judgment
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

    try:
        promtp = jugement_ques_prompt.format(question=question, crt_ans=crt_ans, stu_ans=stu_ans)
        messages = [{"role": "system",
                     "content": "你是一名阅卷老师，负责对学生的答案进行打分和评价"},
                    {"role": "user", "content": promtp}]

        return_result = LLM(messages)

        content = {
            'content': return_result,
            'status': 1}

        return jsonify(content)
    except:
        return jsonify({'content': f'未知错误，', 'status': -1})







