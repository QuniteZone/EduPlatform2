import requests
import numpy as np


EmbedModel_auth_token="sk-ppzjdoyclsjocxncdmbytziuaiobxcrpfxkejzorhmxkmtxd"
EmbedModel_api_url="https://api.siliconflow.cn/v1/embeddings"
RerankModel_auth_token="sk-ppzjdoyclsjocxncdmbytziuaiobxcrpfxkejzorhmxkmtxd"
RerankModel_api_url="https://api.siliconflow.cn/v1/rerank"


def encode_model(input_text):
    payload = {
        "model": "BAAI/bge-large-zh-v1.5",
        "input": input_text,
        "encoding_format": "float"
    }
    headers = {
        "Authorization": f"Bearer {EmbedModel_auth_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(EmbedModel_api_url, json=payload, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        embedding = json_response['data'][0]['embedding']
        return np.array(embedding), None
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response text:", response.text)
        return None, response.text


def rerank_model(query, documents):
    payload = {
        "model": "BAAI/bge-reranker-v2-m3",
        "query": query,
        "documents": documents,
        "top_n": len(documents),
        "return_documents": False,
        "max_chunks_per_doc": 1024,
        "overlap_tokens": 80
    }
    headers = {
        "Authorization": f"Bearer {RerankModel_auth_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(RerankModel_api_url, json=payload, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        scores = [result['relevance_score'] for result in json_response['results']]
        return scores, None
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response text:", response.text)
        return None, response.text


def rerank_results(results, query_vector):
    texts = [result[1] for result in results]
    ranks, error = rerank_model(query_vector, texts)
    if error:
        return results  # Return original results in case of error
    sorted_indices = np.argsort(ranks)[::-1]
    return [results[i] for i in sorted_indices]

# 使用示例
# 假设 user_input 是用户的输入
user_input = "Apple"
query_vector, _ = encode_model(user_input)

# 假设 index 是已建立的 Faiss 索引
k = 5
distances, indices = index.search(query_vector.reshape(1, -1), k)

# 假设 get_indexed_data() 返回一组索引数据
indexed_data = get_indexed_data()
results = [(indexed_data[i][0], indexed_data[i][1]) for i in indices[0] if i < len(indexed_data)]

# 对结果进行重排序
reranked_results = rerank_results(results, user_input)
