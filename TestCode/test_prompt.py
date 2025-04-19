import os
import openai
import re

#
os.environ["OPENAI_BASE_URL"] = "https://api.chatanywhere.tech"
os.environ["OPENAI_API_KEY"] = "sk-QBFgXmIcXeaR5v40BZN3jabFKtSkoudkpIz4vmGU6V8Uu4N6"
model='gpt-3.5-turbo'
temperature=0.5


def format_lesson_plan(text):
    # 使用正则表达式提取被 ```markdown 和 ``` 包裹的内容
    match = re.search(r'```markdown\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        # 提取匹配到的内容并去掉前后的空白
        return match.group(1).strip()
    else:
        return False

def LLM(model,messages):
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

        # 解析 JSON 内容
        result = format_lesson_plan(content)

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


if __name__ == '__main__':

    subject = "高数"
    book = "人民教育出版社高中数学必修一"
    question_type = "不限"
    grade = "高一"
    topic = "导数"
    difficulty = "不限"
    num = "10"
    knowledge = "导数定义，导数的基本法则，导数的应用，高阶导数"
    others = "给出参考答案"


    prompt = f"""
    
    请根据以下输入生成相应的试题内容。

## 输入模块
- **学科**：{subject}学科名称（如：数学、物理、语文等）
- **教材名称**：{book}教材版本或名称（如：人民教育出版社高中数学必修一）
- **题型**（可选项）：{question_type}不限 / 选择题 / 填空题 / 计算题
- **年级**：{grade}适用的学生年级（如：大一、高二、初三等）
- **主题**：{topic}题目所属的教学主题（如：导数、牛顿运动定律、文言文阅读等）
- **难度**{difficulty}（可选项）：不限 / 简单 / 中等 / 困难
- **题量**：{num}需要生成的题目数量（如：5题、10题等）
- **知识点**：{knowledge}试题应覆盖的关键知识点（如：函数求导、力的分解、人物形象分析等）
- **其他要求**：{others}任何补充说明或特殊需求（如：需包含详细步骤、贴近生活情




 境、符合高考题风格等）

## 生成逻辑
- 依据题型与难度进行题干构建，确保题目符合认知水平与教学阶段；
- 准确围绕所选知识点设计设问，突出关键能力考查；
- 每道题目配备标准参考答案，表述清晰，格式规范；
- 若未明确题型或难度，默认生成题型多样、难度适中的组合题组；
- 输出统一采用 Markdown 格式，内容包含题干与参考答案，除非另有说明不包含解析。

## 输出格式规范
{{  

**题目编号（题型，难度）**  
题干内容（可含数学公式、图文材料、现实情境等）  

**参考答案**：答案内容（包括文字表达、数学表达式、解题过程等）

}}

    
    """

    messages = [{"role": "system",
                 "content": "你是一个资深的教育工作者，你需要按照用户的要求生成生成相应的试题内容。"},
                {"role": "user", "content": prompt}]


    message = LLM(model, messages=messages)
    print(message)