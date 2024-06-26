from typing import List,Dict
import os
from dotenv import load_dotenv
from pinecone import Pinecone
import numpy as np
import json
import logging
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# 환경 변수 로드
load_dotenv()
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# Pinecone 초기화
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'e5-model'
index = pc.Index(index_name)


#  모델 로드
name = 'intfloat/multilingual-e5-large'
tokenizer = AutoTokenizer.from_pretrained(name)
model = AutoModel.from_pretrained(name) 


###  백터 변환 
def text_to_vector(text: str)  -> List[float]:
    
   
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True , max_length=512)    # 
    outputs = model(**inputs)
    
    vector = outputs.last_hidden_state[:,0,:].squeeze().detach().numpy()
    
    return vector.tolist()


def recipe_to_vector(recipe: Dict) -> List[float]:
    
    # ingredients 필드의 키만 사용하여 문자열로 변환
    ingredients_keys = " ".join(recipe['ingredients'].keys()) if 'ingredients' in recipe and isinstance(recipe['ingredients'], dict) else ""
         
    # koBert : 단어 위주의 임베딩 
    text = f"{recipe.get('title', '')} {recipe.get('author', '')} {recipe.get('platform', '')} {ingredients_keys} {recipe.get('instructions', '')}"
    
    vector = text_to_vector(text)
    
    print(f"임베딩 벡터 차원: {len(vector)}")  # 임베딩 벡터 차원을 출력
    
    return vector


# # 예제 사용법
# example_recipe = {
#     "title": "스파게티까르보나라",
#     "author": "뚝딱이형",
#     "platform": "chef kim의 뚝딱레시피",
#     "ingredients": {"스파게티": "200g", "달걀": "2", "베이컨": "100g"},
#     "instructions": "스파게티를 익히고 베이컨을 굽는다.달걀 후라이를 만들어 올린다."
# }

# vector = recipe_to_vector(example_recipe)



# 백터 검색    
def search_pinecone(query: str, top_k : int = 10) -> List[Dict]:
    
    #RoBERTa 벡터 생성
    vector = text_to_vector(query)
    
    # Pinecone에서 검색
    response = index.query(vector=vector, top_k=top_k, include_metadata=True)
    results = []
    
    for match in response['matches']:
        metadata = match['metadata']
        # ingredients 필드가 문자열일 경우 딕셔너리로 변환
        if isinstance(metadata.get('ingredients', ''), str):
            metadata['ingredients'] = json.loads(metadata['ingredients'])
        results.append({
            'title': metadata.get('title', ''),
            'ingredients': list(metadata.get('ingredients', {}).keys()) if isinstance(metadata.get('ingredients', {}), dict) else [],
            'instructions': metadata.get('instructions', '')
        })
    
    return results


# 배치 처리함수 : 백터 데이터를 100 사이즈로 나누어 업로드 (크기가 크기때문에 저장이 안되어서 나눔)
def batch_upsert(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i+batch_size]
        index.upsert(vectors=batch)
        logging.info(f'Upserted batch of size: {len(batch)}')
        
        

        






