import requests

###测试聊天功能
# 准备要发送的数据
data = {
    "image_urls": [
        "https://94686t61i9.zicp.fun//static/LLM/files/1b1d33ad-37ad-497e-9735-4cd973cf3ecf.png",  # 替换为你的图片 URL
        "https://94686t61i9.zicp.fun//static/LLM/files/e2a733cc-2459-4b5b-815e-c2f493d98ccd.png"  # 替换为你的图片 URL
    ],
    "message": "请分析给出这道题目的详细解题思路。"  # 用户消息
}
url_2="http://192.168.31.171:5001/ques/chat"
# 发送 POST 请求
# 发起POST请求，设置stream=True以实现流式响应
response = requests.post(url_2, json=data, stream=True)

# 检查响应状态
if response.status_code == 200:
    # 逐行读取响应内容
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))  # 打印每一行内容