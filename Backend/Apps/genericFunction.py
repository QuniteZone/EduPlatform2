#### 该文件用于存放各蓝图功能所通用功能函数、提示词等信息
import json
import os
import re

import docx
import fitz
import openai
import requests
from Apps.ragflow_operations import RAGflow
from Apps.config import model,temperature,ragflow_BASE_URL,ragflow_API_KEY,LLMs_ALLOWED_IMAGE_EXTENSIONS,LLMs_ALLOWED_FILE_EXTENSIONS,LLMs_model,web_video_url,web_message_url,web_api_key
import Apps.config


ALLOWED_EXTENSIONS = {'pdf', 'docx'} #在生成逐字稿时，所允许上传的文件类型
ragflow = RAGflow(ragflow_BASE_URL,ragflow_API_KEY)

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
        if result == False:
            print("JSON 解析失败，重试中...")
            print(f"content:{content}")
        if result:
            return result
        else:
            # 如果 JSON 解析失败，提供反馈并重试
            if is_json:
                feedback = "请返回严格的 JSON 格式"
            else:
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

def LLMs_StreamOutput(messages,is_json=True):
    # 初始化OpenAI客户端
    client = openai.OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""  # 定义完整回复
    is_answering = False  # 判断是否结束思考过程并开始回复

    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model=LLMs_model,
        messages=messages,
        stream=True,
        # 解除以下注释会在最后一个chunk返回Token使用量
        # stream_options={
        #     "include_usage": True
        # }
    )

    # print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    # yield "\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n"
    print("<think>")
    yield "<think>"

    for chunk in completion:
        # 如果chunk.choices为空，则打印usage
        if not chunk.choices:
            print("\nUsage:")
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            # 打印思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                print(delta.reasoning_content, end='', flush=True)
                yield delta.reasoning_content
                reasoning_content += delta.reasoning_content
            else:
                if delta.content != "" and not is_answering:
                    # print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    # yield "\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n"
                    print("</think>")
                    yield "</think>"
                    is_answering = True
                yield delta.content
                print(delta.content, end='', flush=True)
                answer_content += delta.content


def LLM_StreamOutput(messages):
    response = openai.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
        max_tokens=4095,
        stream=True  # 启用流式输出
    )

    # 提取模型返回的内容
    content = response.choices[0].message.content

    # 逐步提取模型返回的内容
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end='', flush=True)  # 实时输出内容

    return content



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(path):
    import PyPDF2
    text = ''
    try:
        pdf = fitz.open(stream=path.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()
    except Exception as e:
        text = f"[PDF解析失败]: {str(e)}"
    return text

def extract_text_from_docx(path):
    text = ''
    try:
        doc = docx.Document(path)
        for para in doc.paragraphs:
            text += para.text + '\n'
    except Exception as e:
        text = f"[Word解析失败]: {str(e)}"
    return text



def LLMs_allowed_file(filename, file_type):
    if file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in LLMs_ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'file':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in LLMs_ALLOWED_FILE_EXTENSIONS
    return False



##定义实时网络访问检索的函数
def get_globalWeb_source(input_content):
    # 构造请求的payload
    # payload_video = json.dumps({
    #     "q": input_content,
    #     "gl": "cn",
    #     "hl": "zh-cn",
    #     "num": 10,
    #     "page": 1
    # })
    payload_message = json.dumps({
        "q": f"site:csdn.net OR site:zhihu.com OR site:cnblogs.com OR site:jianshu.com  {input_content}",
        "gl": "cn",
        "hl": "zh-cn",
        "num": 25
    })

    headers = {
        'X-API-KEY': web_api_key,
        'Content-Type': 'application/json'
    }

    # # # 整理视频信息
    # response_video = requests.request("POST", web_video_url, headers=headers, data=payload_video)
    # json_content = response_video.json()
    # videos = json_content['videos']
    # sorted_videos = []
    # for video in videos:
    #     video_info = {
    #         'title': video.get('title'),
    #         'link': video.get('link'),
    #         'introduce': video.get('snippet'),
    #         'duration': video.get('duration'),
    #         'source': video.get('source'),
    #         'date': video.get('date'),
    #         'position': video.get('position'),
    #         'imageUrl': video.get('imageUrl'),
    #         'is_video': 1,
    #     }
    #     sorted_videos.append(video_info)


    ## 文本网络实时资源检索
    response_message = requests.request("POST", web_message_url, headers=headers, data=payload_message)
    json_content=response_message.json()
    # 整理资源信息
    resources = json_content['organic']
    sorted_messages = []
    for resource in resources:
        title = resource.get('title')
        link = resource.get('link')
        snippet = resource.get('snippet')
        position = resource.get('position')

        # 整理成字典
        sorted_messages.append({
            'title': title,
            'link': link,
            'introduce': snippet,
            'position': position,
            'is_video':0,
        })
    return  None,sorted_messages


# result,result2=get_globalWeb_source("Python编程")
# print("*"*50)
# print(result)
# print("*"*50)
# print(result2)
# print("*"*50)
#
# # 输出整理后的资源
# for video in result:
#     print(f"位置: {video['position']}")
#     print(f"标题: {video['title']}")
#     print(f"链接: {video['link']}")
#     print(f"简介: {video['introduce']}")
#     print(f"时长: {video['duration']}")
#     print(f"来源: {video['source']}")
#     print(f"日期: {video['date']}")
#     print(f"图片链接: {video['imageUrl']}")
#     print("\n" + "-" * 40 + "\n")
#
# print("#"*50)
# for res in result2:
#     print(f"位置: {res['position']}\n标题: {res['title']}\n链接: {res['link']}\n简介: {res['introduce']}\n")




######## 下面为提示词设计 #######
## 教案提示词
## 教案提示词
lesson_plan_prompt = """
 
一，任务描述：
请为{grade}，{subject}，{knowledge}，设计一份内容丰富且完整的教案。
二，输出要求:
# 格式规范
1. 使用Markdown代码块符号返回
2. 字段顺序固定为：[输入模块,知识库检索,生成逻辑,输出样例]
3. 每个教学环节必须包含：
- 教学程序（具体到教师语言示例）
- 设计意图（结合建构主义/最近发展区等教学理论）
4. 数学符号使用LaTeX格式
5. 每个层级的键名必须与示例完全一致（如"教学年级"不可改为"年级"）输出格式需要严格按照如下格式来，此外不要输出其他任何内容！输出的内容用{{}}包裹。

```markdown
# 教学设计方案：

## 一、课程标准

- **教学主题**：课程的主题或核心知识点 
- **适用情境**：面向{grade}年级的{subject}课堂，适用于xxx具体教学阶段（例如：初学阶段、深入探讨阶段等），帮助学生理解xxx核心知识点或技能
- **教学内容**：包括xxx教学内容的核心概念或知识点，同时涵盖其实际应用或具体实例，引导学生将理论与实践结合  
- **教学目标**：  
  输入本节课希望学生达到的预期学习成果，包括知识、能力、情感等方面
  - 理解xxx教学内容的基本概念与要点  
  - 能够在实际生活或课堂学习中应用xxx教学内容
  - 培养学生的xxx关键能力，如批判性思维、问题解决能力、合作能力等
- **课时安排**：n课时（约m分钟） （输入课时n和课时长度m）

## 二、教学设计
### 1. 新课导入

- **教学程序**：  
给出一个具体的可执行的脚本。例如，
  - 通过引导学生思考与生活中相关的现象或问题来激发兴趣，如：“你们在日常生活中有遇到过xxx相关问题或现象吗？”  
  - 提问引导或播放短视频、展示图片等，帮助学生引入xxx教学内容的相关背景或知识
  - ...

- **设计意图**：  
细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因
  - 例如，“激发学生对新知识的兴趣，并通过生活化的情境使他们感知到知识的实际意义，建立学生对新课的认同感和学习动力。”
  - ...

### 2. 自主学习

- **教学程序**：  
给出一个具体的可执行的脚本。例如，
  - 学生通过课本、网络资源或教师提供的材料，进行自主学习，深入理解xxx教学内容
  - 学生思考并记录重要问题，如：  
    1. xxx知识点的定义是什么？  
    2. 它如何在实际中得到应用？  
    3. 学生认为掌握这一知识的意义何在？  
    4. ...

- **设计意图**：  
细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因
  - 例如，“培养学生独立获取知识的能力，并通过思考和探讨帮助他们形成对知识的深入理解，激励学生的探究精神。”
  - ...

### 3. 案例分析

- **教学程序**：  
给出一个具体的可执行的脚本。例如，
  - 教师提供相关的案例或情境（如：“在xxx相关领域中，如何运用xxx知识点来解决实际问题？”），并引导学生分析  
  - 学生小组合作讨论，解决实际问题后进行汇报，并与全班分享思路和结果
  - ...

- **设计意图**： 
细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因
  - 例如， “通过具体案例让学生看到知识的实际应用，增强学生的分析与解决问题的能力，同时在小组合作中锻炼团队协作与交流能力。”
  - ...

### 4. 学习评价

- **教学程序**：  
给出一个具体的可执行的脚本。例如，
  - 教师通过思维导图或小测验等方式帮助学生回顾学习内容  
  - 学生进行自评和互评，总结自己的收获并对学习过程进行反思，教师给予反馈
  - ...

- **设计意图**：  
细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因
  - 例如，“ 帮助学生回顾所学内容，评估他们对知识点的掌握程度，激励他们进行自我反思，促进更深层次的知识内化。”\
  - ...

---

### 5. 小结

- **教学程序**：  
给出一个具体的可执行的脚本。例如，
  - 教师总结本课的关键知识点，并引导学生讨论如何将这些知识应用到其他学科或实际问题中  
  - 提出开放性问题或引导性问题，让学生思考：如何将今天学到的知识应用到生活中？
  - ...

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因
  - 例如，“巩固课堂所学的知识，并帮助学生将知识系统化，培养他们将学到的知识运用于其他领域的能力。”
  - ...

### 6. 作业布置

- **教学程序**：  
给出一个具体的可执行的脚本。例如，
  - 任务一：完成与本课相关的练习或思考题  
  - 任务二：选择一个实际案例，分析xxx知识点在其中的应用，并准备报告或展示材料
  - ...

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因
  - 例如，“通过课后任务强化学生对知识点的理解与应用，激发他们的独立思考和分析能力，同时为学生提供实践的机会。”
  - ...

---

## 三、素养目标
给出一个具体的内容。例如，
- **学科素养**：理解并掌握xxx知识点的核心概念，能够在实际问题中进行有效应用  
- **技术与应用能力**：能够将所学知识运用于具体问题的解决中，进行数据分析、方案设计等  
- **创新与批判性思维**：能够从多角度分析问题，提出独立且创新的解决方案  
- **合作与表达**：能够在小组合作中有效沟通、清晰表达个人观点并进行反馈交流
- ...

```
 
       """

# 班会稿生成提示词
class_meeting_prompt = """
一，任务描述：
请为{grade}年级，围绕{knowledge}的主题与要求，设计一份内容丰富且完整的班会稿。
二，输出要求:
# 格式规范
1. 使用Markdown代码块符号返回
2. 字段顺序固定为：[主题模块,环节设计,实施逻辑,示例模板]
3. 每个环节必须包含：
- 实施流程（具体到主持人语言示例）
- 教育意图（结合群体动力学/社会情感学习理论）
4. 每个层级的键名必须与示例完全一致
5. 输出内容用{{}}包裹

```markdown
# 主题班会设计方案：

## 一、核心要素

- **班会主题**：具体主题名称
- **适用对象**：{grade}年级学生，适用于xx学期阶段/特殊时间节点  
- **教育目标**：  
  - 认知层面：帮助学生理解xxx核心概念 
  - 情感层面：培养xxxx目标情感态度 
  - 行为层面：引导学生实践xxxxx具体行动指南 
- **时长规划**：n分钟（建议45-60分钟）

## 二、实施流程
### 1. 情境创设

- **实施流程**：  
  - 开场白示例："同学们，最近我们注意到xxxxx相关现象，今天让我们共同探讨..."  
  - 播放短视频/展示图片/情景剧表演  
  - 抛出引导性问题："如果遇到xxx情景，你会如何应对？"

- **教育意图**：  
  - 通过具象化场景引发情感共鸣  
  - 运用认知冲突理论激发思考

### 2. 主题研讨

- **实施流程**：  
  - 分组讨论规则说明："每组6人，选出记录员和发言人"  
  - 提供结构化讨论框架：  
    1. 现象分析：xxx相关问题的现状  
    2. 影响评估：对个人/集体的潜在影响  
    3. 策略构建：可行的解决方案

- **教育意图**：  
  - 应用合作学习理论深化认知  
  - 培养批判性思维和协商能力

### 3. 情景模拟

- **实施流程**：  
  - 设计角色扮演场景："假设你是xxx角色，面对xxx冲突情境..."  
  - 准备道具和背景材料  
  - 组织观众评议："哪种处理方式更恰当？为什么？"

- **教育意图**：  
  - 通过具身认知强化学习效果  
  - 提升换位思考和问题解决能力

### 4. 承诺践行

- **实施流程**：  
  - 制作"行动卡片"填写个人计划  
  - 组织集体宣誓仪式  
  - 布置实践任务："下周请完成一次xxx具体行动"

- **教育意图**：  
  - 运用承诺一致性原理促进行为转化  
  - 建立同伴监督支持机制

---

### 5. 总结提升

- **实施流程**：  
  - 播放学生反思视频片段  
  - 教师升华总结："今天我们共同认识到..."  
  - 齐诵班级公约相关条款

- **教育意图**：  
  - 强化价值观认同  
  - 建立持续的行为规范

## 三、延伸方案
- **家校联动**：设计家长反馈卡/亲子互动任务  
- **后续追踪**：制定xxx周期的成效评估方案  
- **资源支持**：推荐相关书籍/公众号/心理热线
 
"""


## 逐字稿提示词 已经弃用，已经放到RAGflow中使用
script_gen_prompt= """
一，任务描述：你需要基于用户提供的教案信息和课程教材相关内容，撰写一份教师上课的逐字稿。
    下面是教案内容
    {teachPlan}        
    以上是教案内容。
    以下是对应教材内容
    {textbook}
    以上是对应教材内容
    逐字稿要求：要求你根据教案的环节、课本教材内容具体来设计一堂课的逐字稿脚本，大约设计好40分钟的脚本。其他教师要求：{require}

二、示例
严格按照如下格式进行输出，不允许输出其他多余内容
```markdown
### 高中数学导数课程教学逐字稿
#### 一、课程引入（5分钟）

**杨老师**：同学们，大家好！今天我们要学习朱自清的散文《背影》。在这篇作品中，朱自清细腻地描写了父爱的伟大与细腻。首先，我想问问大家，有没有经历过与父亲告别的时刻？那种感觉是什么样的？
**学生**：我上次跟父亲去旅行，临别的时候有点伤感。
**学生**：我记得上次放假回家时，父亲送我到车站，我们在那儿告别。
**杨老师**：非常好！这些经历都和《背影》的主题相呼应。为了帮助大家更好地理解这篇文章，我们先来了解一下朱自清的生平和写作背景。
---

#### 二、自主学习（10分钟）
**杨老师**：接下来，请大家阅读《背影》，并思考以下问题：第一，文章中有哪些细节描写让你感受到父爱的？第二，朱自清是如何通过语言传达情感的？第三，你认为这篇文章对你有什么启发？请大家记录下你们的思考，准备在小组中分享。
（学生阅读文章，思考并记录）
**杨老师**：好，现在请各小组进行讨论，分享你们的观点。

---
#### 三、案例分析（10分钟）
**杨老师**：在你们的小组讨论中，大家对哪一段落印象最深刻？
**学生**：我们讨论了父亲去买橘子那一段，感觉特别感人。
**杨老师**：很好，请你们分享一下这段的情感表达和写作手法。
**学生**：那一段写得很细腻，朱自清用“背影”和“冬天”来暗示父亲为我做的牺牲，而且描述了父亲的动作细节，使我深刻感受到他当时的心情。
**杨老师**：对，这样的细节描写让我们更能感受到父爱的深厚。不仅如此，朱自清用一些比喻和对比的手法，增强了情感的表现。请大家选择一个段落进行详细分析，并准备好汇报。
（各小组进行分析汇报）
---
#### 四、学习评价（5分钟）
**杨老师**：大家通过小组讨论，加深了对《背影》的理解。现在请我们一起回顾一下这篇散文的主要情感与写作特色。大家认为，这篇文章中最重要的情感是什么？

**学生**：是父爱的伟大与牺牲精神。
**杨老师**：非常准确！我们可以通过思维导图的方式，一起总结一下今天的学习内容。请大家现在进行自评，总结一下自己的理解。
（学生进行自评，老师巡视并给予反馈）
```
    """


## 评价题目提示词
jugement_ques_prompt = """
    一，任务描述：你是一名阅卷老师，负责对学生的答案进行打分和评价。我将给出题目、学生答案和参考答案，参考答案中除了答案之外还会有该题的给分点以及该题的总分。
你的任务是识别出学生作答的内容，并针对学生回答的正确性给出适当的评分，并针对学生回答的正确性给出评价，要求以老师语境，评价全面客观，能反映学生的学习情况和知识点掌握情况，每个评价的字数都要不少于20字，不超过50字。 
请注意学生作答的内容不包含题干。 请注意给分的规则：按照一般规则或者关键点给分。如果没有作答，则给零分。 
    你需要基于用户提供的题目，学生答案和参考答案，合理给出评分和评价。
        下面是题目
        {question}        
        以上是题目
        以下是对应的学生答案
        {stu_ans}
        以上是对应的学生答案
        下面是参考答案
        {crt_ans}
        上面是对应的参考答案

    二，输出格式
    请直接回复一个json字符串对象，对象具有两个属性：属性'ai_score'表示你的打分，对应的值是一个数字；属性'ai_comment'是对这个学生答案的评价，对应的值是一个字符串。不要有其他多于内容。
        输出格式需要严格按照如下格式来，且请确保你的输出能够被Python的json.loads函数解析，此外不要输出其他任何内容！
        ```json
            {{
                "ai_score": "表示你的打分，对应的值是一个数字",
                "ai_comment": ”对这个学生答案的评价，对应的值是一个字符串“,
            }}
        ```
        """


#出题提示词
generate_question_prompt = """
一，任务描述：
请为{grade}年级，设计一份包含{question_count}道题目的{subject}学科的题目，题目类型为{question_type}，难度为{difficulty}，围绕{knowledge_points}知识点展开，确保题目数量与需求一致，并输出解析与标准答案。
用户其他要求：{other_requirements}

二，输出要求:
# 格式规范
1. 使用Markdown代码块符号返回
2. 字段顺序固定为：[题目模块,知识库检索,生成逻辑,输出样例]
3. 每个题目必须包含：
- 题目正文（具体到题目内容）
- 选项/答案（如果适用，包括正确答案和解析）
4. 数学符号使用LaTeX格式
5. 每个层级的键名必须与示例完全一致
6. 输出内容用```markdown   ```包裹起来
7. 使用{question_type}任务类型的模板进行题目的生成，确保难度适应{grade}年级水平，同时与{subject}学科紧密结合。

三，知识点检索
知识点：根据提供的{knowledges}进行知识点的检索，确保题目符合相关知识要求。


四、示例
下面是输出示例，严格按照如下格式来输出。不允许有其他任何类型
```markdown
**题目1**：一个矩形的长是8厘米，宽是5厘米，求这个矩形的周长。(2分)  
A. 20厘米  
B. 26厘米
C. 40厘米  
D. 30厘米  
**答案:** A  
**解析:** 矩形周长的计算公式为：周长 = 2 × (长 + 宽) = 2 × (8 + 5) = 26厘米。

---

**题目2**：一个正方形的边长为6米，求它的面积。(2分)  
**答案:** 36平方米  
**解析:** 正方形面积的计算公式为：面积 = 边长 × 边长 = 6 × 6 = 36平方米。

---

**题目3**：一块草地的长度是12米，宽度是4米，草地的面积是多少平方米？(2分)  
**答案:** 48平方米  
**解析:** 草地的面积计算公式为：面积 = 长 × 宽 = 12 × 4 = 48平方米。
```

"""







