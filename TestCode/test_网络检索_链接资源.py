import requests
import json

# url = "https://google.serper.dev/search"
#
# payload = json.dumps({
#   "q": "机器学习资源",
#   "gl": "cn",
#   "hl": "zh-cn",
#   "num": 20
# })
# headers = {
#   'X-API-KEY': '54933bde17093ecd3db9ef1d25f16be7c3a5a6d2',
#   'Content-Type': 'application/json'
# }
#
# response = requests.request("POST", url, headers=headers, data=payload)
#
# json_content=response.json()

json

# 整理资源信息
resources = json_content['organic']
sorted_resources = []

for resource in resources:
    title = resource.get('title')
    link = resource.get('link')
    snippet = resource.get('snippet')
    position = resource.get('position')

    # 整理成字典
    sorted_resources.append({
        'title': title,
        'link': link,
        'snippet': snippet,
        'position': position
    })

# 输出整理后的资源
for res in sorted_resources:
    print(f"位置: {res['position']}\n标题: {res['title']}\n链接: {res['link']}\n简介: {res['snippet']}\n")
