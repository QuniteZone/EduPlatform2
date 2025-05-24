#### 该文件用于存放各蓝图功能所通用功能函数、提示词等信息
import json
import os
import re
import time
import pandas as pd
import numpy as np
from joblib import load
import docx
import fitz
import openai
import requests
from Apps.DKT.KnowledgeTracing.evaluation.run import predict_with_trained_model
from Apps.ragflow_operations import RAGflow
from config.config import model, temperature, ragflow_BASE_URL, ragflow_API_KEY, LLMs_ALLOWED_IMAGE_EXTENSIONS, \
    LLMs_ALLOWED_FILE_EXTENSIONS, LLMs_model, web_video_url, web_message_url, web_api_key
import config.config

ALLOWED_EXTENSIONS = {'pdf', 'docx'}  # 在生成逐字稿时，所允许上传的文件类型
ragflow = RAGflow(ragflow_BASE_URL, ragflow_API_KEY)

#这是测试函数，用于测试知识追踪模型 用于没有接入贵兰在线，故单个学生做题数据存放在EduPlatform2/Backend/static
def student_knowledge():
    pkl_path=os.path.join('static','dkt_model_final.pth')

    #获得学生的各个知识点掌握情况
    knowledge_states= predict_with_trained_model(pkl_path)[0]

    #读取知识点具体描述“知识点库.xls”，将其余知识点掌握情况对应起来
    DataK_path=os.path.join('static','知识点库.xls')
    df = pd.read_excel(DataK_path, sheet_name='output')  # 使用工作表名称
    combined_list = []
    for idx, knowledge in enumerate(df['label']):
        # print(f"{idx}: {knowledge}")
        combined_list.append((knowledge, float(knowledge_states[idx]))) #知识点 掌握情况权重。共计534个知识点

    return combined_list


def divide_learning_style():
    pkl_path=os.path.join('static','student_learning_style_model.pkl')

    print(f"pkl:{pkl_path}")

    # 加载模型
    model = load(pkl_path)

    # 构造一个学生的特征数据
    # 输入示例 ['task_0_ratio'（任务类型0在全部中的占比）, 'task_1_ratio'（任务类型2在全部中的占比）, 'task_2_ratio', 'task_3_ratio', 'task_4_ratio',
    #      'task_5_ratio', 'average_study_time'（平均学习时间）, 'course_completion_rate'（课程完成率）,
    #      'study_time_21_6_ratio'（在21-6时学习的概率）, 'study_time_7_20_ratio'（在7-20时学习的概率）]
    # 任务类型 (0=图文，1=视频，2=音频，3=讨论，4=文档，5=PPT)
    new_data = np.array([
        [0, 0.40625, 0, 0, 0, 0.40625, 1120.057142857143, 0.9142857142857143, 0.9142857142857143, 0.08571428571428572]
    ])

    # 预测
    prediction = model.predict(new_data)[0]
    # 输出
    print("预测结果：", prediction)

    # 定义映射
    learning_time_map = {
        0: "深夜学习型",
        1: "日间学习型",
        2: "全时段学习型"
    }
    task_type_map = {
        0: "视觉导向型",
        1: "听觉导向型",
        2: "读写导向型",
        3: "多元导向型"
    }
    efficiency_map = {
        0: "高效学习型",
        1: "低效学习型"
    }

    def parse_result(result):
        try:
            learning_time = learning_time_map.get(result[0], "未知类型")
            task_type = task_type_map.get(result[1], "未知类型")
            efficiency = efficiency_map.get(result[2], "未知类型")
            return f"学习时间段分布: {learning_time}, 任务类型分布: {task_type}, 学习效率: {efficiency}"
        except:
            return "无特定学习风格"

    # 调用解析函数
    parsed_output = parse_result(prediction)

    return parsed_output
    # 输出示例 预测结果： [[0 0 0]]
    # 按照学习时间段分布：深夜学习型【0】，日间学习型【1】，全时段学习型【2】
    # 按照任务类型分布：视觉导向型【0】，听觉导向型【1】，读写导向型【2】，多元导向型【3】
    # 按照学习时长和完成率分布：高效学习型【0】，低效学习型【1】



def format_lesson_plan(text, is_json):
    if is_json:
        # 使用正则表达式提取被 ```json 和 ``` 包裹的内容
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            # 提取匹配到的内容并去掉前后的空白
            json_str = match.group(1).strip()
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

def LLM(messages, is_json=True):
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        # 调用 OpenAI API
        response = openai.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            max_tokens=16384,
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


def LLMs_StreamOutput(messages, is_json=True):
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
        max_tokens=16000,
        stream=True  # 启用流式输出
    )

    # 提取模型返回的内容
    # content = response.choices[0].message.content

    # 逐步提取模型返回的内容
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(f"data: {content}\n")  # 实时输出内容
            yield f"data: {content}\n"




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(path):
    text = ''
    try:
        with fitz.open(path) as pdf:
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
    json_content = response_message.json()
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
            'is_video': 0,
        })
    return None, sorted_messages


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
请为年级：{grade}，学科：{subject}，教案需求描述：{knowledge}，设计一份内容丰富且完整的教案。
二，输出要求:
格式规范

1. 使用Markdown代码块符号返回
2. 字段顺序固定为：[输入模块,知识库检索,生成逻辑,输出样例]
3. 每个教学环节必须包含：
- 教学程序（具体到教师语言示例）
- 设计意图（结合建构主义/最近发展区等教学理论）
5. 每个层级的键名必须与示例完全一致（如"教学年级"不可改为"年级"）输出格式需要严格按照如下格式来，此外不要输出其他任何内容！输出的内容用{{}}包裹。
6. 严格按照教案需求描述中所包含的字数要求生成对应的字数数量。
7. 可以适当的生成创意内容，不是必须按照参考示例的结构，可以自己生成新的标题。

三、参考示例（内容参考，不要照抄）：
```markdown
# 教学设计方案：

## 一、课程标准

- **教学主题**：课程的主题或核心知识点  
- **适用情境**：面向{grade}年级的{subject}课堂，适用于xxx具体教学阶段，帮助学生理解xxx核心知识点或技能  
- **教学内容**：包括xxx教学内容的核心概念或知识点，同时涵盖其实际应用或具体实例，引导学生将理论与实践结合  
- **教学目标**：  
  输入本节课希望学生达到的预期学习成果，包括知识、能力、情感等方面  
  - 理解xxx教学内容的基本概念与要点  
  - 能够在实际生活或课堂学习中应用xxx教学内容  
  - 培养学生的xxx关键能力，如批判性思维、问题解决能力、合作能力等  
- **课时安排**：n课时（约m分钟）（输入课时n和课时长度m）

## 二、教学设计

### 1. 新课导入

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 教师提问：“同学们，你们有没有观察过天气预报中的温度变化？它跟我们今天要学习的内容有关系哦。”  
  - 播放一段关于气温变化的短视频，引导学生关注数据变化趋势  
  - 引导学生分享自己在生活中遇到的相关现象，建立初步感知  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “通过贴近生活的例子激发学生兴趣，激活已有经验，为新知识的学习打下基础，符合建构主义中‘前认知’的作用机制。”  
  - “视频的引入增强直观感受，提高注意力，有助于学生形成对即将学习内容的期待感。”

### 2. 自主学习

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 学生阅读教材第x页至第y页，完成教师提供的学习任务单  
  - 在小组内交流自学所得，提出疑问并尝试解答  
  - 记录关键知识点，并尝试绘制简单的思维导图进行归纳总结  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “培养学生独立获取信息的能力，促进学生主动建构知识体系，符合维果斯基‘最近发展区’理论中自主探索的要求。”  
  - “通过小组协作讨论，增强同伴之间的互动与反馈，提升学习效率。”

### 3. 合作探究

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 教师提供若干组实验材料（如不同形状的容器、水温计等）  
  - 小组合作完成指定实验任务，记录实验数据并分析结果  
  - 每组派代表汇报探究过程与发现，其他同学可以提问或补充  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “通过动手操作和团队合作，让学生在真实情境中体验科学探究的过程，加深对知识点的理解。”  
  - “鼓励表达与质疑，培养学生的批判性思维与语言组织能力。”

### 4. 知识讲解

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 教师结合学生探究结果，系统讲解相关知识点  
  - 利用板书或PPT展示重点公式、定义及应用场景  
  - 设置即时练习题，检查学生是否理解关键概念  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “教师的系统讲解帮助学生梳理逻辑结构，填补自主探究中可能存在的知识盲点。”  
  - “即时练习能有效检测学生理解程度，便于教师及时调整教学节奏。”

### 5. 案例分析

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 展示一则关于水资源浪费的真实案例（如某地因漏水造成大量水资源损失）  
  - 引导学生思考如何利用所学知识解决该问题  
  - 鼓励学生提出解决方案，并进行全班讨论与优化  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “通过真实案例引导学生将知识迁移到现实问题中，提升综合运用能力。”  
  - “讨论与优化方案的过程有助于学生形成系统化的问题解决思路。”

### 6. 学习评价

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 教师带领学生回顾本课知识点，构建完整的知识网络图  
  - 学生填写自我评估表，反思本节课的学习收获与不足  
  - 开展小组互评，指出同伴的优点与建议  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “帮助学生建立知识的整体框架，增强记忆与理解。”  
  - “通过自评与互评，引导学生进行元认知反思，提升学习策略的有效性。”

### 7. 小结

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 教师总结本节课的重点与难点  
  - 提问引导学生思考：“如果我们将这个知识点应用到其他学科中，比如地理、生物，会发生什么？”  
  - 鼓励学生课后继续查阅资料，拓展视野  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “强化知识点的巩固，帮助学生从整体上把握学习内容。”  
  - “启发跨学科思维，推动深度学习的发生。”

### 8. 作业布置

- **教学程序**：  
  给出一个具体的可执行的脚本。例如，  
  - 完成课本上的练习题，巩固基础知识  
  - 观察家庭用水情况，制作一份节约用水的小报告  
  - 收集三个与本课相关的新闻报道或生活案例，并简要分析其中的科学原理  

- **设计意图**：  
  细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因  
  - “通过书面与实践相结合的作业形式，兼顾知识掌握与能力提升。”  
  - “引导学生关注社会热点，增强社会责任感与实践意识。”

---

## 三、素养目标

- **学科素养**：理解并掌握xxx知识点的核心概念，能够在实际问题中进行有效应用  
- **技术与应用能力**：能够将所学知识运用于具体问题的解决中，进行数据分析、方案设计等  
- **创新与批判性思维**：能够从多角度分析问题，提出独立且创新的解决方案  
- **合作与表达**：能够在小组合作中有效沟通、清晰表达个人观点并进行反馈交流  
- **社会责任与价值观**：能够在解决问题的过程中体现环保意识、公平意识与可持续发展理念  
- **数字素养与信息处理能力**：能够合理使用信息技术手段收集、整理与呈现学习成果  
- **终身学习能力**：具备自主学习意识，能够制定学习计划并持续改进学习方法

```

       """

# 班会稿生成提示词
class_meeting_prompt = """
一，任务描述：
请为{grade}年级，围绕{knowledge}的主题与要求，设计一份内容丰富且完整的班会稿。
二，输出要求:
# 格式规范
1. 必须使用Markdown代码块符号返回
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

## 逐字稿提示词
script_gen_prompt = """
一，任务描述：你需要基于用户提供的教案信息和课程教材相关内容，撰写一份教师上课的逐字稿。
    教案内容:{teachPlan}        
    以下是对应教材内容
    {textbook}
    以上是对应教材内容
    逐字稿要求：要求你根据教案的环节、课本教材内容具体来设计一堂课的逐字稿脚本，如果没有时间要求，就设计大约40分钟的脚本。其他教师要求：{require}

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

# 出题提示词
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
4. 数学符号使用markdown格式输出
5. 每个层级的键名必须与示例完全一致
6. 输出内容用```markdown   ```包裹起来
7. 使用{question_type}任务类型的模板进行题目的生成，确保难度适应{grade}年级水平，同时与{subject}学科紧密结合。
8. 严格按照题量数：{question_count}生成对应的题目数量，不允许省略。
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


##个性化推荐 提示词
recommendation_prompt = """
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
    1. 学习路径应包括多个阶段，每个阶段有明确的学习目标和时间安排，需要分析任务的难易，综合划分合理的不同阶段。总阶段数保持在至少两个及以上。
    2. 每个阶段应包含至少两个学习任务，每个任务应包括任务名称、任务描述、所需资源、在线资源等。
    3. 学习路径应考虑到不同学习风格的需求，如视觉型学习者应优先考虑视频教程和图片资料等。
    4. 学习路径应尽可能涵盖用户需要掌握的所有知识点，并确保每个知识点都有相应的学习任务。
    5. 学习路径应提供实际可行的建议，帮助用户在实际操作中提升学习效果。
    8. 学习路径应考虑到用户的实际需求，例如，如果用户要求规定在一周内完成任务，则整体任务必须规定在一周内。
    9. 学习路径应尽可能提供多样化的学习资源，如在线课程、书籍、视频等。
    10.从选用的任何online_source内容，都需要原内容输出。不允许修改、不允许遗漏。
    11.输出tasks的resources部分和online_source部分不允许为空，其中online_source至少需要有三个。另外online_source必须选择两个及以上的视频资源个数。
    12.video_summary只需要包含视频中简介内容，并且不允许缺失，需要提取关于视频简介的全部内容。其余内容无需提取。
    13.提取的tags需要包含"tags"建的所有值，不允许遗漏，修改等操作。
    14.检索的资源不能够出现重复以及混乱组合。

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

