#### 该文件用于存放各蓝图功能所通用功能函数、提示词等信息
import json
import os
import re

import docx
import fitz
import openai
from Apps.ragflow_operations import RAGflow
from Apps.config import model,temperature,ragflow_BASE_URL,ragflow_API_KEY,LLMs_ALLOWED_IMAGE_EXTENSIONS,LLMs_ALLOWED_FILE_EXTENSIONS,LLMs_model
import Apps.config


ALLOWED_EXTENSIONS = {'pdf', 'docx'} #在生成逐字稿时，所允许上传的文件类型
ragflow = RAGflow(ragflow_BASE_URL,ragflow_API_KEY)

def format_lesson_plan(text,is_json):
    if is_json:
        # 使用正则表达式提取被 ```json 和 ``` 包裹的内容
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            # 提取匹配到的内容并去掉前后的空白
            return match.group(1).strip()
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

    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    yield "\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n"

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
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    yield "\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n"
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


######## 下面为提示词设计 #######
## 教案提示词
lesson_plan_prompt = """
        一，任务描述：
        请你为{grade}，{subject}，{knowledge}，设计一份内容丰富且完整的教案。

        二，输出要求:
        # 格式规范
        1. 使用Markdown代码块符号返回
        2. 字段顺序固定为：[输入模块,知识库检索,生成逻辑,输出样例]
        3. 每个教学环节必须包含：
           - 可执行脚本（具体到教师语言示例）
           - 设计意图（结合建构主义/最近发展区等教学理论）
        4. 数学符号使用LaTeX格式
        5. 每个层级的键名必须与示例完全一致（如"教学年级"不可改为"年级"）输出格式需要严格按照如下格式来，此外不要输出其他任何内容！输出的内容用{{}}包裹。

        ```markdown
        # 教案

## 课程标准

- **教学名称**: 本节课教学名称，名字要简洁且能概括本教案内容
- **教学内容**: 明确本课涉及的知识范畴与核心知识点
- **适用情境**: 说明课程最适合的授课场景与条件限制
- **教学目标**: 本节课希望学生达到的预期学习成果，包括知识、能力、情感等方面
- **核心素养**: 本节课着重培养的学生必备品格和关键能力
- **建议课时**: 根据知识密度与学生基础规划的教学时间分配

## 活动设计

### 新课导入
- **教学程序**: 通过情境创设或问题链激活前备知识，建立新旧知识联结。给出一个具体的可执行的脚本给老师执行。
- **设计意图**: 细致解释本小结设置的意义是什么，并且给出上面部分输出内容具体设计的原因，内容要丰富。

### 自主学习
- **教学程序**: 学生运用导学资源独立完成基础性知识建构的认知过程。给出一个具体的可执行的脚本给老师执行，例如老师提出什么问题让同学讨论。
- **设计意图**: 细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因。

### 案例分析
- **教学程序**: 选取典型实例引导学生运用理论解决问题的探究活动，这个要和"新课导入"、"自主学习"部分的内容相关联。
- **设计意图**: 细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因。

### 学习评价
- **教学程序**: 贯穿课堂的形成性评估与三维目标达成度检测，给出这教案可以通过那几点教学评价。
- **设计意图**: 细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因。

### 小结
- **教学程序**: 结构化梳理知识网络并提炼思维方法的总结环节。
- **设计意图**: 细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因。

### 作业布置
- **教学程序**: 分层设计的巩固型任务与拓展型实践项目。这部分给出具体布置什么作业。
- **设计意图**: 细致解释本小结设置的意义是什么，并且给出"教学程序"部分具体设计的原因。

## 素养培养
本课通过[实验误差分析/文本深度解读]等教学活动，重点发展学生的[学科专属能力]（如物理实验设计能力），同步渗透[跨学科能力]培养（如数据建模思维）。通过[具体教学策略]实现知识迁移，形成[可观测行为指标]（如提出2种实验改进方案），建立从素养培育到评估验证的完整闭环。```
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
```json
    {{
        "title": "### 高中数学导数课程教学逐字稿",
        "content": '''
        #### 一、课程引入（5分钟）

        **老师**：同学们，大家好！今天我们要学习一个非常重要的数学概念——导数。导数在数学和科学中都有着广泛的应用，所以掌握它对你们的学习非常重要。

        **老师**：首先，我们来回顾一下函数的概念。请问，有同学能告诉我什么是函数吗？

        **学生**：函数是一个输入和输出之间的关系，每一个输入对应一个输出。

        **老师**：很好！函数可以用图像、表格或公式来表示。今天我们主要关注的是函数的变化率。我们想知道，当自变量发生微小变化时，函数值是如何变化的。这就是导数的核心思想。

        **老师**：我们先来看一个简单的例子。假设我们有一个函数 \( f(x) = x^2 \)。我们想知道在某一点 \( x = a \) 处，函数的变化率是多少。我们可以通过计算切线的斜率来找到这个变化率。

        **老师**：那么，什么是切线呢？切线是与曲线在某一点相切的直线。它的斜率就代表了该点的瞬时变化率。我们可以用极限的方式来定义导数。

        （同学们思考5分钟）

        ---

        #### 二、导数定义讲解（10分钟）

        **老师**：导数的定义是这样的：  
        \[f'(a) = \lim_{{h \\to 0}} \frac{{f(a+h) - f(a)}}{{h}}\]  
        这个公式的意思是，当 \( h \) 趋近于 0 时，\( \frac{{f(a+h) - f(a)}}{{h}} \) 的极限就是函数 \( f \) 在点 \( a \) 处的导数。

        **老师**：现在我们来实际计算一下 \( f(x) = x^2 \) 在 \( x = 2 \) 处的导数。首先，我们需要计算 \( f(2+h) \) 和 \( f(2) \)。

        **老师**：我们知道，\( f(2) = 2^2 = 4 \)。接下来，计算 \( f(2+h) \)：  
        \[ f(2+h) = (2+h)^2 = 4 + 4h + h^2 \]

        **老师**：现在我们将这些值代入导数的定义中：  
        \[ f'(2) = \lim_{{h \\to 0}} \frac{{(4 + 4h + h^2) - 4}}{{h}} = \lim_{{h \\to 0}} \frac{{4h + h^2}}{{h}} \]

        **老师**：我们可以将 \( h \) 提出来：  
        \[ f'(2) = \lim_{{h \\to 0}} (4 + h) \]

        **老师**：当 \( h \) 趋近于 0 时，\( f'(2) = 4 \)。所以，函数 \( f(x) = x^2 \) 在 \( x = 2 \) 处的导数是 4。

        ---

        #### 三、导数的几何意义（5分钟）

        **老师**：那么，导数的几何意义是什么呢？导数实际上表示了函数图像在某一点的切线斜率。我们可以通过图像来理解这一点。

        **老师**：例如，在 \( f(x) = x^2 \) 的图像上，\( x = 2 \) 处的切线斜率为 4，这意味着在这一点上，函数的变化率是 4。也就是说，当 \( x \) 增加 1 时，\( f(x) \) 的值大约增加 4。

        ---

        #### 四、导数的应用（10分钟）

        **老师**：导数在实际生活中有很多应用。比如，在物理学中，导数可以用来描述物体的速度和加速度。

        **老师**：假设我们有一个物体的位移函数 \( s(t) \)，它表示物体在时间 \( t \) 时的位置。物体的速度就是位移函数的导数：  
        \[ v(t) = s'(t) \]

        **老师**：如果我们知道物体的位移函数是 \( s(t) = 5t^2 \)，那么我们可以计算物体在任意时刻的速度。首先，我们计算导数：  
        \[ v(t) = s'(t) = \lim_{{h \\to 0}} \frac{{s(t+h) - s(t)}}{{h}} = \lim_{{h \\to 0}} \frac{{5(t+h)^2 - 5t^2}}{{h}} \]

        **老师**：经过计算，我们得到：  
        \[ v(t) = 10t \]  
        这意味着物体的速度与时间成正比。

        ---

        #### 五、课堂练习（5分钟）

        **老师**：现在我们来做一个小练习。请大家计算一下函数 \( f(x) = 3x^3 \) 在 \( x = 1 \) 处的导数。

        （学生进行计算，老师巡视）

        **老师**：谁能告诉我你们的答案？

        **学生**：导数是 9。

        **老师**：很好！我们来验证一下。首先计算 \( f(1) \) 和 \( f(1+h) \)：  
        \[ f(1) = 3(1)^3 = 3 \]  
        \[ f(1+h) = 3(1+h)^3 = 3(1 + 3h + 3h^2 + h^3) = 3 + 9h + 9h^2 + 3h^3 \]

        **老师**：将这些代入导数的定义中，计算得出：  
        \[ f'(1) = \lim_{{h \\to 0}} \frac{{(3 + 9h + 9h^2 + 3h^3) - 3}}{{h}} = \lim_{{h \\to 0}} (9 + 9h + 3h^2) = 9 \]

        ---

        #### 六、总结与提问（5分钟）

        **老师**：今天我们学习了导数的定义、计算方法以及它的几何意义和应用。导数是一个非常重要的概念，掌握它将对你们的学习和未来的应用有很大帮助。

        **老师**：在结束之前，有没有同学对今天的内容有疑问或者想要进一步探讨的地方？

        （学生提问，老师解答）

        **老师**：如果没有问题，大家可以回去复习一下导数的定义和计算方法，准备下节课的内容。谢谢大家的参与！

        ''',
    }}
```

三，输出格式
    输出格式需要严格按照如下格式来，且请确保你的输出能够被Python的json.loads函数解析，此外不要输出其他任何内容！
    ```json
        {{
            "title": "逐字稿的标题，数学导数课程教学逐字稿",
            "content": '''关于逐字稿的主要内容，格式采用标准的markdown格式''',
        }}
    ```
    """


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


