import requests

# 设置请求的 URL
url = 'http://127.0.0.1:5001/plan/study_plan'  # 修改为您的 Flask 应用运行的地址

# 构造请求数据
data = {
    'goal': '学习数字素养基础内容知识。例如编程基础、开源教育',
    'background': '我在数学方面有一定的基础',
    'preferences': '我喜欢通过做题来学习',
    'time': '40小时',
    'deadline': '2025-06-30',
    'title': '数学学习计划'
}

# 发送 POST 请求
response = requests.post(url, json=data)

# 打印响应结果
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.json()}")
