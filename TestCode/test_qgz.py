



import requests

###测试聊天功能
import requests

url_2 = "https://94686t61i9.zicp.fun/ques/chat"

while True:
    # 获取用户输入
    user_content=input("请输入消息：")
    # user_content = "我的用户昵称是什么？"

    # 检查用户是否想退出
    if user_content.lower() == 'exit':
        print("退出程序。")
        break

    user_message=[
        {
            'role':'user',
            'content':"我的用户名称是QuniteZone，你需要记住。另外你需要快速回复我",
        },
        {
            'role':'assistant',
            'content':"好的，QuniteZone！我会记住你的名字并尽量快速回复你。有什么我可以帮你的吗？"
        },
        {
            'role':'user',
            'content':user_content
        }
    ]


    # 准备数据
    data = {
        "image_urls": [
            # "https://94686t61i9.zicp.fun//static/LLM/files/1b1d33ad-37ad-497e-9735-4cd973cf3ecf.png",  # 替换为你的图片 URL
        ],
        "message": user_message  # 用户消息
    }

    # 发送 POST 请求
    response = requests.post(url_2, json=data, stream=True)

    if response.status_code == 200:
        # 初始化变量
        think_content = ""
        other_content = ""
        inside_think = False  # 用于跟踪是否在 <think> 标签内
        buffer = ""  # 用于暂存 <think> 标签内的内容

        # 逐行读取响应内容
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')  # 解码每一行
                print(f"{decoded_line}")  # 打印当前行内容

                # 检查是否包含 <think> 标签
                if "<think>" in decoded_line:
                    # 找到 <think> 标签的起始位置
                    start_index = decoded_line.index("<think>") + len("<think>")
                    buffer += decoded_line[start_index:].strip() + "\n"  # 收集内容
                    inside_think = True  # 进入 <think> 状态

                elif "</think>" in decoded_line and inside_think:
                    # 找到 </think> 标签的结束位置
                    end_index = decoded_line.index("</think>")
                    # 将 buffer 中的内容添加到 think_content
                    think_content += buffer.strip() + "\n"  # 完成 <think> 内容的收集
                    buffer = ""  # 清空缓冲区
                    inside_think = False  # 退出 <think> 状态

                    # 将 </think> 标签后面的内容添加到 other_content
                    other_content += decoded_line[end_index + len("</think>"):].strip() + "\n"

                elif inside_think:
                    # 如果在 <think> 标签内，继续收集内容
                    buffer += decoded_line.strip() + "\n"
                else:
                    # 其他内容
                    other_content += decoded_line.strip() + "\n"


        # 打印提取的内容
        print(f"用户提问：{user_message}\n################")
        print(f"思考过程：{think_content}\n###################")
        print(f"完整回复内容:{other_content}\n#################")




    else:
        print(f"请求失败，状态码: {response.status_code}")
