import os
import uuid
from openai import OpenAI
from flask import Blueprint, jsonify, request, stream_with_context, Response
from werkzeug.utils import secure_filename

from .genericFunction import LLMs_allowed_file,LLMs_StreamOutput
from .config import LLMs_IMAGE_UPLOAD_FOLDER,LLMs_FILE_UPLOAD_FOLDER,Public_ip,LLMs_model

ques_handle_bp = Blueprint('ques_handle', __name__)




@ques_handle_bp.route('/get_LLM_key', methods=['GET'])
def get_LLM_key():
    key = os.environ["OPENAI_API_KEY"]
    print(f"key:{key}")
    return jsonify({"api_key": key})


#####多模态的问题问答
@ques_handle_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"content": "没有文件上传", 'status': 0})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"content": "没有选择文件", 'status': -1})

    # 确定文件类型并保存
    if file and LLMs_allowed_file(file.filename, 'image'):
        # 生成唯一的文件名
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path=f"{LLMs_FILE_UPLOAD_FOLDER}/{unique_filename}"
        file.save(file_path)
        fileIP=f"{Public_ip}/{file_path}"
        return jsonify({"content": "图片上传成功", "fileIP": fileIP, 'status': 1})
    elif file and LLMs_allowed_file(file.filename, 'file'):
        # 生成唯一的文件名
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path = f"{LLMs_FILE_UPLOAD_FOLDER}/{unique_filename}"
        file.save(file_path)
        fileIP = Public_ip + file_path
        print(f"file fileIP:{fileIP}")
        return jsonify({"content": "文件上传成功", "fileIP": fileIP, 'status': 1})
    else:
        return jsonify({"content": "不支持的文件类型", 'status': -2})


@ques_handle_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    image_urls = data.get('image_urls')  # 从请求中获取图片URL，至少是一个空list
    # files_urls = data.get('files_urls')  # 从请求中获取文件的URL
    user_message = data.get('message')  # 从请求中获取用户消息及历史记录

    user_mesg = user_message[-1]['content']  # 获取最新一条的用户消息提问
    del user_message[-1]

    content_images = []  # 构建最新一条的user提问消息内容
    if image_urls != []:
        for image_url in image_urls:
            obj_img = {
                "type": "image_url",
                "image_url": {"url": image_url},
            }
            content_images.append(obj_img)
    content_images.append({"type": "text", "text": user_mesg})

    # 创建聊天完成请求
    messages=[]
    for message in user_message:
        if message['role']=="user":
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message['content'],
                    }
                ]
            })
        else:
            messages.append(message)


    messages.append({
        "role": "user",
        "content": content_images})

    print(f"最终message:{messages}")

    response = Response(stream_with_context(LLMs_StreamOutput(messages)), content_type='text/plain')

    return response







