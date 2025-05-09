# import requests
#
# # 设定要请求的 URL（请确保该 URL 是正确的，取决于您 Flask 应用的运行地址）
# url = 'http://127.0.0.1:5001/plan/lesson_upload'  # 根据您的 Flask 服务器修改
#
# # 指定要上传的文件路径
# file_path = 'document.pdf'  # 替换为您要上传的文件的路径
#
# # 使用 'with open' 语句读取文件
# with open(file_path, 'rb') as f:
#     # 构建文件数据字典
#     files = {'file': f}
#     # 发送 POST 请求
#     response = requests.post(url, files=files)
#
# # 打印响应内容
# print(response.json())

#
import requests

url = 'http://127.0.0.1:5001/plan/lesson_script'  # 根据您的 Flask 服务器和实际路径调整

# 要发送的数据
data = {
    'require': '40分钟，逐字稿！'  # 根据需要填写
}

# 要上传的文件
files = {
    'files': open('教学设计方案.docx', 'rb')
}

# 发起 POST 请求
response = requests.post(url, data=data, files=files)

# 检查响应
if response.ok:
    print("响应内容:", response.json())
else:
    print("请求失败，状态码:", response.status_code, "内容:", response.text)



