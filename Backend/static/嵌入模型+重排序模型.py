EmbedModel_auth_token = "sk-ppzjdoyclsjocxncdmbytziuaiobxcrpfxkejzorhmxkmtxd"
EmbedModel_api_url = "https://api.siliconflow.cn/v1/embeddings"
RerankModel_auth_token = "sk-ppzjdoyclsjocxncdmbytziuaiobxcrpfxkejzorhmxkmtxd"
RerankModel_api_url = "https://api.siliconflow.cn/v1/rerank"


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
