##封装好了RAGflow相关接口，可以直接调用了对应接口
import json
import requests
import time
import os

class RAGflow:
    def __init__(self,ragflow_BASE_URL, ragflow_API_KEY):
        self.HEADERS = {
            "Authorization": f"Bearer {ragflow_API_KEY}",
            "Content-Type": "application/json"
        }
        self.BASE_URL = ragflow_BASE_URL
        self.API_KEY = ragflow_API_KEY

    def create_dataset(self, name: str, description: str = "") -> str:
        """
        创建数据集，返回 dataset_id
        """
        timestamp = int(time.time())
        unique_name = f"{name}_{timestamp}"

        url = f"{self.BASE_URL}/api/v1/datasets"
        payload = {
            "name": unique_name,
            "description": description
        }

        response = requests.post(url, headers=self.HEADERS, json=payload)
        data = response.json()

        if data.get("code") == 0:
            dataset_id = data["data"]["id"]
            return dataset_id
        else:
            raise Exception(f"创建数据集失败: {data}")

    def upload_and_parse_documents(self, dataset_id: str, file_paths: list) -> list:
        """
        批量上传文档到指定数据集并自动解析
        """
        # 1. 上传文档
        upload_url = f"{self.BASE_URL}/api/v1/datasets/{dataset_id}/documents"
        document_ids = []

        try:
            for file_path in file_paths:
                with open(file_path, 'rb') as file:
                    # 使用files参数上传文件
                    response = requests.post(
                        upload_url,
                        headers={"Authorization": f"Bearer {self.API_KEY}"},
                        files={'file': (os.path.basename(file_path), file)}
                    )

                    if response.status_code != 200:
                        raise Exception(f"上传失败，状态码: {response.status_code}, 响应: {response.text}")

                    data = response.json()

                    if data.get("code") != 0:
                        raise Exception(f"上传失败: {data}")

                    document_id = data["data"][0]["id"]
                    document_ids.append(document_id)
                    print(f"文档上传成功: {document_id}")

            # 2. 触发解析
            parse_url = f"{self.BASE_URL}/api/v1/datasets/{dataset_id}/chunks"
            parse_payload = {
                "document_ids": document_ids
            }

            parse_response = requests.post(parse_url, headers=self.HEADERS, json=parse_payload)
            parse_data = parse_response.json()

            if parse_data.get("code") != 0:
                raise Exception(f"解析触发失败: {parse_data}")

            print("批量文档解析已触发")
            return document_ids

        except Exception as e:
            raise Exception(f"批量上传和解析过程中出错: {str(e)}")

    def get_file_paths(self, folder_path: str) -> list:
        """
        获取指定文件夹中的所有文件路径列表
        """
        file_paths = []

        # 遍历文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

        return file_paths

    def get_files_is_running(self, dataset_id: str, orderby: str = "create_time", desc: bool = True, keywords: str = "", document_id: str = "", document_name: str = ""):
        """
        获取指定数据集中的所有文档解析状态
        返回的json中，run结果分为："DONE"，表示文档解析已完成；"RUNNING"，表示文档解析仍在进行中；'UNSTART'，表示文档未解析，'run': 'FAIL'表示文本解析失败
        """
        try:
            documents = []
            status_docs = True
            page = 1
            page_size = 10
            while status_docs:
                url = f"{self.BASE_URL}/api/v1/datasets/{dataset_id}/documents?page={page}&page_size={page_size}&orderby={orderby}&desc={str(desc).lower()}&keywords={keywords}&id={document_id}&name={document_name}"
                response = requests.get(url, headers=self.HEADERS)

                if response.status_code != 200:
                    raise Exception(f"获取文档状态失败，状态码: {response.status_code}, 响应: {response.text}")

                data = response.json()
                if data.get("code") != 0:
                    raise Exception(f"获取文档状态失败: {data}")

                current_docs = data["data"]["docs"]  # 注意这里是 "docs"
                if current_docs == []:
                    status_docs = False
                else:
                    page += 1
                    documents += current_docs

            is_has_running = False
            # 遍历文档信息并判断状态
            for document in documents:
                doc_id = document.get("id")
                run_status = document.get("run")
                file_name = document.get("name")

                if run_status == "DONE":
                    status_message = "文档解析已完成"
                elif run_status == "RUNNING":
                    status_message = "文档解析仍在进行中"
                    is_has_running = True
                elif run_status == "UNSTART":
                    status_message = "文档未解析"
                elif run_status == "FAIL":
                    status_message = "文本解析失败"
                else:
                    status_message = "未知状态"

                # print(f"文件名：{file_name}  \n文档ID: {doc_id}, 状态: {status_message}")
            return is_has_running, documents

        except Exception as e:
            raise Exception(f"获取文档解析状态过程中出错: {str(e)}")

    def create_chat_assistant(self, name: str, avatar: str, dataset_ids: list, llm: dict, prompt: dict):
        """
        创建聊天助手，返回助手的ID
        """
        url = f"{self.BASE_URL}/api/v1/chats"

        # 构建请求体
        payload = {
            "name": name,  # 会话助手名称，必填
            "avatar": avatar,  # 头像64位编码
            "dataset_ids": dataset_ids,  # 关联数据集
            "llm": llm,  # 大模型设置
            "prompt": prompt  # 提示内容
        }

        # 发送POST请求
        response = requests.post(url, headers=self.HEADERS, json=payload)
        data = response.json()

        # 检查响应状态
        if data.get("code") == 0:
            assistant_id = data["data"]["id"]
            return assistant_id
        else:
            raise Exception(f"创建聊天助手失败: {data}")

    def create_chat_session(self, assistant_id: str, name: str, user_id: str = None) -> str:
        """
        创建与聊天助手的会话，返回会话的ID
        """
        url = f"{self.BASE_URL}/api/v1/chats/{assistant_id}/sessions"

        # 构建请求体
        payload = {
            "name": name
        }

        if user_id:
            payload["user_id"] = user_id

        # 发送POST请求
        response = requests.post(url, headers=self.HEADERS, json=payload)
        data = response.json()

        # 检查响应状态
        if data.get("code") == 0:
            session_id = data["data"]["id"]
            return session_id
        else:
            raise Exception(f"创建会话失败: {data}")

    def send_chat_message(self, assistant_id: str, question: str, stream: bool = False, session_id: str = None, user_id: str = None):
        """
        向指定的聊天助手提问以开始 AI 驱动的对话，返回助手的回答和会话信息
        """
        url = f"{self.BASE_URL}/api/v1/chats/{assistant_id}/completions"

        # 构建请求体
        payload = {
            "question": question,
            "stream": stream
        }

        if session_id:
            payload["session_id"] = session_id
        if user_id:
            payload["user_id"] = user_id

        # 发送POST请求
        response = requests.post(url, headers=self.HEADERS, json=payload)

        # 检查响应状态码
        if response.status_code == 200:
            if stream:
                lines = response.iter_lines()
                line_list = []  # 用于存储所有行
                for line in lines:
                    if line:  # 过滤掉空行
                        decoded_line = line.decode("utf-8")
                        line_list.append(decoded_line)  # 将解码后的行添加到列表中

                # 检查 line_list 是否有足够的行
                if len(line_list) < 2:
                    raise Exception("流式响应中没有足够的行来提取数据")

                # 提取倒数第二行
                second_last_data = line_list[-2]

                # 提取 JSON 部分
                json_part = second_last_data.split("data:")[1]  # 获取提取 JSON 部分 "data:" 后面的部分
                data_object = json.loads(json_part)  # 解析 JSON 字符串为字典对象
                return data_object["data"]["answer"].replace("\n\n", "\n")
            else:
                response_data = response.json()  # 直接解析为JSON
                return response_data["data"]["answer"].replace("\n\n", "\n")
        else:
            raise Exception(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")


    def create_agent_session(self, agent_id: str, user_id: str = None,important_para=None) -> str:
        """
        创建与代理的会话，返回会话的ID
        """
        url = f"{self.BASE_URL}/api/v1/agents/{agent_id}/sessions"

        # 构建请求体
        payload = {}  # 将其他参数作为请求体的一部分

        if important_para !=None:#遍历important_para对象，将参数添加到payload中
            for key, value in important_para.items():
                payload[key] = value

        # 如果提供了 user_id，则将其添加到请求参数中
        if user_id:
            url += f"?user_id={user_id}"

        # 发送POST请求
        response = requests.post(url, headers=self.HEADERS, json=payload)
        data = response.json()

        # 检查响应状态
        if data.get("code") == 0:
            session_id = data["data"]["id"]
            return session_id
        else:
            raise Exception(f"创建会话失败: {data}")

    def delete_agent_session(self, agent_id: str, session_id) -> dict:
        """
        删除与代理关联的会话
        :param agent_id: 代理的 ID
        :param session_ids: 要删除的会话 ID 列表
        """
        url = f"{self.BASE_URL}/api/v1/agents/{agent_id}/sessions"
        session_ids=[session_id]
        # 构建请求体
        payload = {
            "ids": session_ids
        }

        # 发送 DELETE 请求
        response = requests.delete(url, headers=self.HEADERS, json=payload)
        data = response.json()

        # 检查响应状态
        if data.get("code") == 0:
            return {"status": "success", "message": "会话删除成功"}
        else:
            raise Exception(f"删除会话失败: {data}")


    def send_agent_message(self, agent_id: str, question: str, stream: bool = True, session_id: str = None, user_id: str = None):
        """
        向指定的代理提问以开始 AI 驱动的对话，返回代理的回答和会话信息
        """
        url = f"{self.BASE_URL}/api/v1/agents/{agent_id}/completions"

        # 构建请求体
        payload = {
            "question": question,
            "stream": stream
        }

        if session_id:
            payload["session_id"] = session_id
        if user_id:
            payload["user_id"] = user_id

        # 发送POST请求
        response = requests.post(url, headers=self.HEADERS, json=payload)

        # 检查响应状态码
        if response.status_code == 200:
            if stream:
                lines = response.iter_lines()
                line_list = []  # 用于存储所有行
                for line in lines:
                    if line:  # 过滤掉空行
                        decoded_line = line.decode("utf-8")
                        line_list.append(decoded_line)  # 将解码后的行添加到列表中

                # 检查 line_list 是否有足够的行
                if len(line_list) < 2:
                    raise Exception("流式响应中没有足够的行来提取数据")

                # 提取倒数第二行
                second_last_data = line_list[-2]

                # 提取 JSON 部分
                json_part = second_last_data.split("data:")[1]  # 获取提取 JSON 部分 "data:" 后面的部分
                data_object = json.loads(json_part)  # 解析 JSON 字符串为字典对象
                return data_object["data"]["answer"].replace("\n\n", "\n")
            else:
                response_data = response.json()  # 直接解析为JSON
                return response_data["data"]["answer"].replace("\n\n", "\n")
        else:
            raise Exception(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")




# #使用示例
# ragflow_BASE_URL = "http://127.0.0.1"  # rag_flow的后端地址
# ragflow_API_KEY="ragflow-NhN2I5ODZhMTg0MzExZjA4OThkNWFiZW" #qgz 的api key密钥
# ragflow = RAGflow(ragflow_BASE_URL,ragflow_API_KEY)
# TextbookRetr_AgentID="8249059c1a9011f0ae7f9213fbf6b9fc"
#
# agent_session_id = ragflow.create_agent_session(TextbookRetr_AgentID)
#
# # 进行代理Agent聊天
# question = "qinguo1"
# response_data = ragflow.send_agent_message(TextbookRetr_AgentID, question, stream=False, session_id=agent_session_id)
#
#
#
# # 删除该Agent会话
# ragflow.delete_agent_session(TextbookRetr_AgentID, agent_session_id)






# # # 示例使用
# if __name__ == "__main__":
#     ragflow_BASE_URL = "http://127.0.0.1"  # rag_flow的后端地址
#     ragflow_API_KEY="ragflow-NhN2I5ODZhMTg0MzExZjA4OThkNWFiZW" #qgz 的api key密钥
#     ragflow = RAGflow(ragflow_BASE_URL,ragflow_API_KEY)
#     # 创建数据集、上传文档、创建聊天助手、创建会话等操作
#
#     dataset_id = f"4f34a594192d11f093b942e643a9908f"  # 知识库ID
#     assistant_id = f"395418f2192f11f0988f42e643a9908f"  # 会话助手ID
#     assistan_session_id = f"4f432590192f11f0b3ad42e643a9908f"  # 聊天会话的ID
#     #### 示例使用
#     # # 1. 创建数据集
#     if dataset_id == None:
#         dataset_id = ragflow.create_dataset("测试数据集2", "上传文档并解析测试")
#         print(f"成功创建知识库，dataset_id: {dataset_id}")
#
#     # # 2. 上传并解析文档
#     # folder_path = f"D:/projcet_LLM/EduPlatform/Backend/static/ragflowParserDocs"
#     # file_paths = ragflow.get_file_paths(folder_path)
#     # document_id = ragflow.upload_and_parse_documents(dataset_id, file_paths)
#
#
#     # 3.获取所有文档解析最新状态
#     # 获取文档解析状态
#     is_has_running, documents = ragflow.get_files_is_running(dataset_id)  # is_has_running为bool true表示有文件处于解析中 false则没有处于解析中
#     # 打印文档解析状态
#     print(f"获取文件状态：{is_has_running}")
#     for document in documents:
#         print(f"文档ID: {document['id']}, 状态: {document['run']}")
#
#     # 4. 创建聊天助手
#     dataset_ids = [dataset_id]
#     if assistant_id == None:
#         name = "新聊天助手qgz"
#         prompt = {
#             "empty_response": "抱歉！知识库中未找到相关内容！",
#             "keywords_similarity_weight": 0.7,
#             "opener": "你好！ 我是你的助理，有什么可以帮到你的吗？",
#             "prompt": """你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。回答需要考虑聊天历史。
#             以下是知识库：
#             {knowledge}
#             以上是知识库。""",
#             "similarity_threshold": 0.2,
#             "top_n": 6,
#             "variables": [{"key": "knowledge", "optional": False}]
#         }
#         llm = {
#             "model_name": "gpt-4o-mini",
#             "temperature": 0.1,
#             "top_p": 0.3,
#             "presence_penalty": 0.4,
#             "frequency_penalty": 0.7
#         }
#         avatar = "None"  # 头像
#         assistant_id = ragflow.create_chat_assistant(name, avatar, dataset_ids, llm, prompt)
#         print(f"聊天助手创建成功，助手ID: {assistant_id}")
#
#     # 5.创建聊天会话
#     session_name = "新会话Code"
#     if assistan_session_id == None:
#         assistan_session_id = ragflow.create_chat_session(assistant_id, session_name)
#         print(f"会话创建成功，会话ID: {assistan_session_id}")
#
#     # #6.进行聊天会话
#     # question = "给我一份校赛挑战杯平台简易使用教程"
#     # response_data = ragflow.send_chat_message(assistant_id, question, stream=False, session_id=assistan_session_id)
#     # print(f"助手的回答: {response_data}")
#
#     agent_session_id = f"813972c0192f11f09a5942e643a9908f"
#     agent_id = "92c366ca192211f086c742e643a9908f"
#     ##注意，agent需要提前在web端的RAGflow构建好，提供好对应的agent ID
#     # 7.构建代理Agent会话
#     if agent_session_id == None:
#         agent_session_id = ragflow.create_agent_session(agent_id)
#         print(f"Agent会话创建成功，会话ID: {agent_session_id}")
#
#     # 8.进行代理Agent聊天
#     question = "给我一份校赛挑战杯平台简易使用教程"
#     response_data = ragflow.send_agent_message(agent_id, question, stream=False, session_id=agent_session_id)
#     print(f"助手的回答: {response_data}")
