import json
import os
import re

import openai

#
os.environ["OPENAI_BASE_URL"] = "https://api.chatanywhere.tech"
os.environ["OPENAI_API_KEY"] = "sk-QBFgXmIcXeaR5v40BZN3jabFKtSkoudkpIz4vmGU6V8Uu4N6"
model='gpt-3.5-turbo'
temperature=0.5


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

        # 提取模型返回的内容
        content = response.choices[0].message.content

        # 解析 JSON 或 markdown 内容
        result = format_lesson_plan(content, is_json)

        if result:
            return result
        else:
            # 如果 JSON 解析失败，提供反馈并重试
            feedback = "请返回严格的 Markdown 格式"
            messages.append({
                "role": "assistant",
                "content": content
            })
            messages.append({
                "role": "user",
                "content": feedback
            })
            retry_count += 1
            print(f"第 {retry_count} 次尝试")
    return False

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




if __name__ == '__main__':
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