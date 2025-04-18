# from openai import OpenAI
import openai
import os


os.environ["DASHSCOPE_API_KEY"] = "sk-b8ee8eb0b16a4f8099a7492bdbe405c9"
llm_name="qvq-max"

def LLMs(message):
    # 初始化OpenAI客户端
    client =openai.OpenAI(
        api_key = os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""     # 定义完整回复
    is_answering = False   # 判断是否结束思考过程并开始回复

    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model=llm_name,
        messages=message,
        stream=True,
        # 解除以下注释会在最后一个chunk返回Token使用量
        # stream_options={
        #     "include_usage": True
        # }
    )

    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

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
                reasoning_content += delta.reasoning_content
            else:
                # 开始回复
                if delta.content != "" and is_answering is False:
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                # 打印回复过程
                print(delta.content, end='', flush=True)
                answer_content += delta.content
    return answer_content, reasoning_content

messages2=[
    {
            "role": "user",
            "content": [
                {   "type": "image_url",
                    "image_url": {
                    "url": "https://94686t61i9.zicp.fun//static/LLM/files/1b1d33ad-37ad-497e-9735-4cd973cf3ecf.png"}, },
                {"type": "text", "text": "分析图片内容？"},
            ],
        },
]

messages3=[{'role': 'user', 'content': [{'type': 'image_url', 'image_url': {'url': 'https://94686t61i9.zicp.fun//static/LLM/files/1b1d33ad-37ad-497e-9735-4cd973cf3ecf.png'}}, {'type': 'image_url', 'image_url': {'url': 'https://94686t61i9.zicp.fun//static/LLM/files/e2a733cc-2459-4b5b-815e-c2f493d98ccd.png'}}, {'type': 'text', 'text': '请分析给出这道题目的详细解题思路。简短一些'}]}]


LLMs(messages3)