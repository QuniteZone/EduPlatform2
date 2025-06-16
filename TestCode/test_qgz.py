import requests

# 设置请求的URL
url = "http://127.0.0.1:5001/user/course_data"

# 设置请求的payload数据
data = {
    "student_id": "1830475870539571200"
}


# 发送POST请求
response = requests.get(url, data=data)

# 打印响应结果
print("状态码:", response.status_code)
print("响应内容:", response.json())
