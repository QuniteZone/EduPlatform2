import requests

# 定义目标 URL
url = 'http://192.168.31.172:5001/plan/lesson_script'  # 替换为你的服务器地址

# 定义要上传的文件和其他表单数据
files = {
    'files': open('ML教案.pdf', 'rb')  # 替换为你的文件路径
}
data = {
    'require': '需要给我生成一份比较详细的逐字稿，时长控制在45分钟左右。'  # 替换为你的 require 值
}

# 发起 POST 请求
response = requests.post(url, files=files, data=data)

# 输出响应内容
print('Response status code:', response.status_code)
print('Response body:', response.text)
