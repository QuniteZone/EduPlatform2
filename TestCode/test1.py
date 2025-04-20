import requests

# 定义请求的 URL
url = "http://192.168.202.16:5001/plan/question_generate"  # 替换为你的实际 URL

# 构造请求数据
data = {
    "subject": "数学",
    "grade": "高二",
    "textbook": "人民教育出版社高中数学必修一",
    "topic": "导数",
    "questionType": "选择题",
    "difficulty": "中等",
    "questionCount": 10,
    "knowledgePoints": "函数求导",
    "otherRequirements": "需包含详细步骤，贴近生活情境"
}

# 发送 POST 请求
response = requests.post(url, json=data)

# 打印响应内容
print("状态码:", response.status_code)
print("响应内容:", response.json())
