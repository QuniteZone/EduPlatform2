import requests
import json


web_video_url = "https://google.serper.dev/videos"
web_message_url="https://google.serper.dev/search"
web_api_key="54933bde17093ecd3db9ef1d25f16be7c3a5a6d2"

##定义访问检索的函数
def get_globalWeb_source(input_content):
    # 构造请求的payload
    payload_video = json.dumps({
        "q": input_content,
        "gl": "cn",
        "hl": "zh-cn",
        "num": 10,
        "page": 1
    })
    payload_message = json.dumps({
        "q": input_content,
        "gl": "cn",
        "hl": "zh-cn",
        "num": 10
    })

    headers = {
        'X-API-KEY': web_api_key,
        'Content-Type': 'application/json'
    }

    # # 整理视频信息
    response_video = requests.request("POST", web_video_url, headers=headers, data=payload_video)
    json_content = response_video.json()
    videos = json_content['videos']
    sorted_videos = []
    for video in videos:
        video_info = {
            'title': video.get('title'),
            'link': video.get('link'),
            'introduce': video.get('snippet'),
            'duration': video.get('duration'),
            'source': video.get('source'),
            'date': video.get('date'),
            'position': video.get('position'),
            'imageUrl': video.get('imageUrl'),
            'is_video': 1,
        }
        sorted_videos.append(video_info)


    ## 文本网络实时资源检索
    response_message = requests.request("POST", web_message_url, headers=headers, data=payload_message)
    json_content=response_message.json()
    # 整理资源信息
    resources = json_content['organic']
    sorted_messages = []
    for resource in resources:
        title = resource.get('title')
        link = resource.get('link')
        snippet = resource.get('snippet')
        position = resource.get('position')

        # 整理成字典
        sorted_messages.append({
            'title': title,
            'link': link,
            'introduce': snippet,
            'position': position,
            'is_video':0,
        })
    return  sorted_videos,sorted_messages


result,result2=get_globalWeb_source("Python编程")
print("*"*50)
print(result)
print("*"*50)
print(result2)
print("*"*50)

# 输出整理后的资源
for video in result:
    print(f"位置: {video['position']}")
    print(f"标题: {video['title']}")
    print(f"链接: {video['link']}")
    print(f"简介: {video['introduce']}")
    print(f"时长: {video['duration']}")
    print(f"来源: {video['source']}")
    print(f"日期: {video['date']}")
    print(f"图片链接: {video['imageUrl']}")
    print("\n" + "-" * 40 + "\n")

print("#"*50)
for res in result2:
    print(f"位置: {res['position']}\n标题: {res['title']}\n链接: {res['link']}\n简介: {res['introduce']}\n")