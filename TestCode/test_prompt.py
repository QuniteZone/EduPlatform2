<<<<<<< HEAD
# import os
# import openai
=======
import json
import os
import re

import openai
>>>>>>> 9104cd3601d81d365121772bf577370912f65d20

# #
# os.environ["OPENAI_BASE_URL"] = "https://api.chatanywhere.tech"
# os.environ["OPENAI_API_KEY"] = "sk-QBFgXmIcXeaR5v40BZN3jabFKtSkoudkpIz4vmGU6V8Uu4N6"
# model='gpt-3.5-turbo'
# temperature=0.5


<<<<<<< HEAD
# def format_lesson_plan(text):
#     # 使用正则表达式提取被 ```markdown 和 ``` 包裹的内容
#     match = re.search(r'```markdown\s*(.*?)\s*```', text, re.DOTALL)
#     if match:
#         # 提取匹配到的内容并去掉前后的空白
#         return match.group(1).strip()
#     else:
#         return False

# def LLM(messages):
#     max_retries = 5
#     retry_count = 0
#     while retry_count < max_retries:
#         # 调用 OpenAI API
#         response = openai.chat.completions.create(
#             model=model,
#             temperature=temperature,
#             messages=messages,
#             max_tokens=4095,
#         )
=======
def format_lesson_plan(text,is_json):
    if is_json:
        # 使用正则表达式提取被 ```json 和 ``` 包裹的内容
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            # 提取匹配到的内容并去掉前后的空白
            json_str=match.group(1).strip()
            try:
                # 将字符串解析为 JSON 对象
                return json.loads(json_str)
            except json.JSONDecodeError:
                return False  # 如果解析失败，返回 False
        else:
            return False
    else:
        # 使用正则表达式提取被 ```markdown 和 ``` 包裹的内容
        match = re.search(r'```markdown\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            # 提取匹配到的内容并去掉前后的空白
            return match.group(1).strip()
        else:
            return False

def LLM(messages,is_json=True):
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        # 调用 OpenAI API
        response = openai.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            max_tokens=4095,
        )
>>>>>>> 9104cd3601d81d365121772bf577370912f65d20

#         # 提取模型返回的内容
#         content = response.choices[0].message.content

<<<<<<< HEAD
#         # 解析 JSON 内容
#         result = format_lesson_plan(content)
=======
        # 解析 JSON 或 markdown 内容
        result = format_lesson_plan(content, is_json)
>>>>>>> 9104cd3601d81d365121772bf577370912f65d20

#         if result:
#             return result
#         else:
#             # 如果 JSON 解析失败，提供反馈并重试
#             feedback = "请返回严格的 Markdown 格式"
#             messages.append({
#                 "role": "assistant",
#                 "content": content
#             })
#             messages.append({
#                 "role": "user",
#                 "content": feedback
#             })
#             retry_count += 1
#             print(f"第 {retry_count} 次尝试")
#     return False

def process_questions(questions):
    prompt=""
    for question in questions:
        prompt+=f"题目ID：{question['ques_ID']   }"
        if question["ques_type"] == "简答题":
            prompt += f"题目：{question['ques_Stem']} 请回答这个简答题。"
        elif question["ques_type"] == "选择题":
            prompt += f"题目：{question['ques_Stem']} 选项是：{question['ques_other']} 请从中选择一个正确的选项。"

        prompt += f" 答案是：{question['ques_answer']}."
        if question["ques_explanation"]:
            prompt += f" 解析：{question['ques_explanation']}"
        #如果不是最后一个
        if question != questions[-1]:
            prompt += "；"

    return prompt




# if __name__ == '__main__':
#     teachPlan = """{{
#         "ActivityDesign": {{
#             "Case_Analysis": {{
#                 "Design_Intent": "通过具体例子帮助学生运用理论知识解决实际问题，增强对数列极限的理解和应用能力，促进理论与实践的结合",
#                 "Teaching_Procedure": "老师：现在我们来看一个具体的例子，数列 $a_n = \\frac{1}{n}$。请大家计算这个数列的极限，并讨论它的收敛特性。你们能找到类似的数列吗？"
#             }},
#             "Homework_Design": {{
#                 "Design_Intent": "通过分层设计的作业，巩固学生对数列极限的理解，同时鼓励他们进行深入思考，提升自主学习能力",
#                 "Teaching_Procedure": "老师：请完成课后习题，特别是第3、4、5题，另外，选一个数列，尝试计算它的极限并写出你的思考过程。"
#             }},
#             "Independent_Learning": {{
#                 "Design_Intent": "鼓励学生自主探索和讨论，增强他们的理解能力，符合最近发展区理论，促进学生在合作中共同进步",
#                 "Teaching_Procedure": "老师：请大家阅读教材中关于数列极限的定义，并思考以下问题：1. 如何判断一个数列是否收敛？2. 极限的几何意义是什么？（分组讨论）"
#             }},
#             "Key_Summary": {{
#                 "Design_Intent": "通过总结和分享促进知识的内化和巩固，帮助学生理清思路，形成系统的知识网络",
#                 "Teaching_Procedure": "老师：我们今天学习了数列的极限，大家可以总结一下极限的定义、性质和判断方法。请各组分享你们的总结。"
#             }},
#             "Learning_Assessment": {{
#                 "Design_Intent": "形成性评估贯穿课堂，能够及时反馈学生的学习情况，帮助教师调整教学策略，以确保学生达到学习目标",
#                 "Teaching_Procedure": "老师：在课堂中，我会通过提问、观察小组讨论情况以及学生的作业完成情况来评估你们对数列极限的理解和掌握程度。"
#             }},
#             "Lesson_Introduction": {{
#                 "Design_Intent": "通过提问激活学生的先前知识，帮助他们建立新旧知识的联系，符合建构主义理论，促进学生的主动思考和参与",
#                 "Teaching_Procedure": "老师：同学们，今天我们来讨论数列的极限。首先，请大家回忆一下什么是数列？（等待学生回答）非常好！那么，数列的极限又是什么呢？（引导学生思考）"
#             }}
#         }},
#         "Competency_Development": "本课通过数列极限的计算与分析等教学活动，重点发展学生的数学逻辑思维能力，促进跨学科能力的培养，如在物理中理解极限的概念。通过小组讨论和案例分析实现知识迁移，形成可观测行为指标，如能够独立解决数列极限问题，建立从素养培育到评估验证的完整闭环。",
#         "CurrStandards": {{
#             "Applicable_Context": "适合于大学一年级的数学课程，课堂设备需具备多媒体教学条件",
#             "Core_Competency": "培养学生的抽象思维、逻辑推理能力和自主学习能力",
#             "Curriculum_Content": "数列的收敛与发散，极限的定义与性质，夹逼定理的应用",
#             "Curriculum_Name": "数列的极限",
#             "Recommended_Sessions": "建议2课时，每课时90分钟",
#             "Teaching_Objectives": "学生能够理解数列极限的概念，掌握极限的计算方法，培养逻辑思维能力和解决问题的能力"
#         }}
#     }}"""

#     textbook="""#### 课程内容：
# 1. **数列的定义**
#    - 数列是一个按照一定顺序排列的数的集合，通常用 \( a_n \) 表示，其中 \( n \) 是正整数。

# 2. **极限的定义**
#    - 数列 \( a_n \) 的极限是指当 \( n \) 趋近于无穷大时，数列的项 \( a_n \) 趋近于某个特定的数 \( L \)。我们记作：
#      \[
#      \lim_{n \to \infty} a_n = L
#      \]
#    - 如果数列的极限存在，则称该数列收敛；如果极限不存在，则称该数列发散。

# 3. **极限的性质**
#    - 如果 \( \lim_{n \to \infty} a_n = L \)，则：
#      - 对于任意的 \( \epsilon > 0 \)，存在正整数 \( N \)，使得当 \( n > N \) 时，\( |a_n - L| < \epsilon \)。
#    - 极限的唯一性：一个数列的极限如果存在，则是唯一的。

# 4. **夹逼定理**
#    - 如果有数列 \( a_n \leq b_n \leq c_n \) 且 \( \lim_{n \to \infty} a_n = \lim_{n \to \infty} c_n = L \)，则 \( \lim_{n \to \infty} b_n = L \)。

# 5. **常见收敛数列的例子**
#    - 数列 \( a_n = \frac{1}{n} \) 收敛于 0。
#    - 数列 \( a_n = \frac{n}{n+1} \) 收敛于 1。"""
#     lesson_plan_prompt = """
#     一，任务描述：你需要基于用户提供的教案信息和课程教材相关内容，撰写一份教师上课的逐字稿。
#         下面是教案内容
#         {teachPlan}        
#         以上是教案内容。
#         以下是对应教材内容
#         {textbook}
#         以上是对应教材内容
#         逐字稿要求：要求你根据教案的环节、课本教材内容具体来设计一堂课的逐字稿脚本，大约设计好40分钟的脚本。其他教师要求：{require}
    
#     二、示例
#     ```json
#         {{
#             "title": "### 高中数学导数课程教学逐字稿",
#             "content": '''
#             #### 一、课程引入（5分钟）
            
#             **老师**：同学们，大家好！今天我们要学习一个非常重要的数学概念——导数。导数在数学和科学中都有着广泛的应用，所以掌握它对你们的学习非常重要。
            
#             **老师**：首先，我们来回顾一下函数的概念。请问，有同学能告诉我什么是函数吗？
            
#             **学生**：函数是一个输入和输出之间的关系，每一个输入对应一个输出。
            
#             **老师**：很好！函数可以用图像、表格或公式来表示。今天我们主要关注的是函数的变化率。我们想知道，当自变量发生微小变化时，函数值是如何变化的。这就是导数的核心思想。
            
#             **老师**：我们先来看一个简单的例子。假设我们有一个函数 \( f(x) = x^2 \)。我们想知道在某一点 \( x = a \) 处，函数的变化率是多少。我们可以通过计算切线的斜率来找到这个变化率。
            
#             **老师**：那么，什么是切线呢？切线是与曲线在某一点相切的直线。它的斜率就代表了该点的瞬时变化率。我们可以用极限的方式来定义导数。
            
#             （同学们思考5分钟）
            
#             ---
            
#             #### 二、导数定义讲解（10分钟）
            
#             **老师**：导数的定义是这样的：  
#             \[f'(a) = \lim_{{h \\to 0}} \frac{{f(a+h) - f(a)}}{{h}}\]  
#             这个公式的意思是，当 \( h \) 趋近于 0 时，\( \frac{{f(a+h) - f(a)}}{{h}} \) 的极限就是函数 \( f \) 在点 \( a \) 处的导数。
            
#             **老师**：现在我们来实际计算一下 \( f(x) = x^2 \) 在 \( x = 2 \) 处的导数。首先，我们需要计算 \( f(2+h) \) 和 \( f(2) \)。
            
#             **老师**：我们知道，\( f(2) = 2^2 = 4 \)。接下来，计算 \( f(2+h) \)：  
#             \[ f(2+h) = (2+h)^2 = 4 + 4h + h^2 \]
            
#             **老师**：现在我们将这些值代入导数的定义中：  
#             \[ f'(2) = \lim_{{h \\to 0}} \frac{{(4 + 4h + h^2) - 4}}{{h}} = \lim_{{h \\to 0}} \frac{{4h + h^2}}{{h}} \]
            
#             **老师**：我们可以将 \( h \) 提出来：  
#             \[ f'(2) = \lim_{{h \\to 0}} (4 + h) \]
            
#             **老师**：当 \( h \) 趋近于 0 时，\( f'(2) = 4 \)。所以，函数 \( f(x) = x^2 \) 在 \( x = 2 \) 处的导数是 4。
            
#             ---
            
#             #### 三、导数的几何意义（5分钟）
            
#             **老师**：那么，导数的几何意义是什么呢？导数实际上表示了函数图像在某一点的切线斜率。我们可以通过图像来理解这一点。
            
#             **老师**：例如，在 \( f(x) = x^2 \) 的图像上，\( x = 2 \) 处的切线斜率为 4，这意味着在这一点上，函数的变化率是 4。也就是说，当 \( x \) 增加 1 时，\( f(x) \) 的值大约增加 4。
            
#             ---
            
#             #### 四、导数的应用（10分钟）
            
#             **老师**：导数在实际生活中有很多应用。比如，在物理学中，导数可以用来描述物体的速度和加速度。
            
#             **老师**：假设我们有一个物体的位移函数 \( s(t) \)，它表示物体在时间 \( t \) 时的位置。物体的速度就是位移函数的导数：  
#             \[ v(t) = s'(t) \]
            
#             **老师**：如果我们知道物体的位移函数是 \( s(t) = 5t^2 \)，那么我们可以计算物体在任意时刻的速度。首先，我们计算导数：  
#             \[ v(t) = s'(t) = \lim_{{h \\to 0}} \frac{{s(t+h) - s(t)}}{{h}} = \lim_{{h \\to 0}} \frac{{5(t+h)^2 - 5t^2}}{{h}} \]
            
#             **老师**：经过计算，我们得到：  
#             \[ v(t) = 10t \]  
#             这意味着物体的速度与时间成正比。
            
#             ---
            
#             #### 五、课堂练习（5分钟）
            
#             **老师**：现在我们来做一个小练习。请大家计算一下函数 \( f(x) = 3x^3 \) 在 \( x = 1 \) 处的导数。
            
#             （学生进行计算，老师巡视）
            
#             **老师**：谁能告诉我你们的答案？
            
#             **学生**：导数是 9。
            
#             **老师**：很好！我们来验证一下。首先计算 \( f(1) \) 和 \( f(1+h) \)：  
#             \[ f(1) = 3(1)^3 = 3 \]  
#             \[ f(1+h) = 3(1+h)^3 = 3(1 + 3h + 3h^2 + h^3) = 3 + 9h + 9h^2 + 3h^3 \]
            
#             **老师**：将这些代入导数的定义中，计算得出：  
#             \[ f'(1) = \lim_{{h \\to 0}} \frac{{(3 + 9h + 9h^2 + 3h^3) - 3}}{{h}} = \lim_{{h \\to 0}} (9 + 9h + 3h^2) = 9 \]
            
#             ---
            
#             #### 六、总结与提问（5分钟）
            
#             **老师**：今天我们学习了导数的定义、计算方法以及它的几何意义和应用。导数是一个非常重要的概念，掌握它将对你们的学习和未来的应用有很大帮助。
            
#             **老师**：在结束之前，有没有同学对今天的内容有疑问或者想要进一步探讨的地方？
            
#             （学生提问，老师解答）
            
#             **老师**：如果没有问题，大家可以回去复习一下导数的定义和计算方法，准备下节课的内容。谢谢大家的参与！

#             ''',
#         }}
#     ```

#     三，输出格式
#         输出格式需要严格按照如下格式来，且请确保你的输出能够被Python的json.loads函数解析，此外不要输出其他任何内容！
#         ```json
#             {{
#                 "title": "逐字稿的标题，数学导数课程教学逐字稿",
#                 "content": '''关于逐字稿的主要内容，格式采用标准的markdown格式''',
#             }}
#         ```
#         """

#     prompt=lesson_plan_prompt.format(teachPlan=teachPlan,textbook=textbook)

#     messages = [{"role": "system",
#                  "content": "你是一个资深的教育工作者，你需要按照用户的要求生成一份专业、有实用价值的教师上课逐字稿。"},
#                 {"role": "user", "content": prompt}]


#     message = predict(model, messages=messages)
#     print(message)
lesson_plan_prompt = """
一，任务描述：
请为{grade}，{subject}，{knowledge}，设计一份内容丰富且完整的教案。
二，输出要求:
# 格式规范
1. 返回严格的Markdown格式；
2. 每个教学环节必须包含：教学程序与设计意图；
3. 数学符号使用LaTeX格式；
4. 仔细检查任务描述，如若其中有涉及教案结构的要求，请按照其要求严格执行；
4. 如若任务描述中未对教案结构作出要求，请参考以下教案模板生成；

```markdown
# 教案

## 一、基本信息

- **课程名称**:  
- **授课教师**:  
- **授课班级**:  
- **授课时间**:  
- **课时安排**:  

---

## 二、教学目标

### 1. 知识与技能目标
- 学生能够掌握哪些知识点。
- 学生能够运用哪些技能解决问题。

### 2. 过程与方法目标
- 通过何种方式引导学生学习（如讨论、实验、案例分析等）。
- 培养学生的哪些能力（如逻辑思维、团队合作、创新意识等）。

### 3. 情感态度与价值观目标
- 引导学生形成怎样的情感态度（如对学科的兴趣、对社会的责任感等）。
- 促进学生形成哪些价值观（如尊重多样性、追求真理等）。

---

## 三、教学重点与难点

### 1. 教学重点
- 列出本节课的核心知识点或技能点。

### 2. 教学难点
- 列出学生可能难以理解或掌握的内容，并简要说明原因。

---

## 四、教学方法

- **教学方法**: （如讲授法、讨论法、探究法、案例教学法等）
- **教学工具**: （如多媒体设备、实验器材、教具等）

---

## 五、教学过程

### 1. 导入环节
- **时间**:  
- **内容**:  
- **活动设计**: （如何吸引学生注意力，引出主题）

### 2. 新授环节
- **时间**:  
- **内容**:  
- **活动设计**: （详细描述知识点讲解、师生互动、小组活动等）

### 3. 巩固练习
- **时间**:  
- **内容**:  
- **活动设计**: （设计练习题或实践活动，帮助学生巩固所学知识）

### 4. 总结提升
- **时间**:  
- **内容**:  
- **活动设计**: （总结本节课的重点内容，提出思考问题或拓展方向）

### 5. 作业布置
- **内容**:  
- **要求**: （明确作业形式、完成时间和提交方式）

---

## 六、板书设计

- **板书内容**:  
- **布局设计**: （可以用简单的文字描述或示意图表示）

---

## 七、教学反思

- **成功之处**:  
- **不足之处**:  
- **改进措施**:  
```
"""
def get_lesson_plan(request):
    grade = request.json.get('grade')
    subject = request.json.get('subject')
    knowledge = request.json.get('knowledge')
    promtp = lesson_plan_prompt.format(grade=grade, subject=subject, knowledge=knowledge)
    messages = [{"role": "system",
                 "content": "你是一个教案生成专家，严格按Markdown格式输出结构化教案内容，确保键值命名与层级关系绝对准确"},
                {"role": "user", "content": promtp}]
    return_result = LLM(messages,is_json=False)
    return return_result

if __name__ == '__main__':
<<<<<<< HEAD
    data = {
    "grade": "高一",
    "subject": "英语",
    "knowledge": "请为朱自清的经典散文《背影》设计一份课时教案，要求教学目标详细到200字左右，字数限制在1200字以内，教案结构清晰，语言流畅，能够有效引导学生理解文章的情感内涵与写作特色，同时注重培养学生的文学鉴赏能力和情感共鸣。"
}
    response = get_lesson_plan(data)
    print(response)

=======
    knowledges_set = [
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
    questions = [
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
    # questions 需要经过一定处理

    # 使用函数处理问题
    ques_output = process_questions(questions) #待解析的题目


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

    print(f"prompt:\n{prompt}")

    messages = [{"role": "system",
                 "content": "你是一个资深的教育工作者，你需要分析用户给出题目中隐含的知识点"},
                {"role": "user", "content": prompt}]


    message = LLM(messages)

    print(message)
    print(message['knowledgeTag'])
>>>>>>> 9104cd3601d81d365121772bf577370912f65d20
