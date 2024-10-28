from typing import List,Dict
import openai
import os
from dotenv import load_dotenv
from pinecone import Pinecone
import numpy as np
import logging


# 환경 변수 로드
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')


#openAI 초기화
openai.api_key = OPENAI_API_KEY
embed_model = 'text-embedding-ada-002'


# Pinecone 초기화
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'recipes'
index = pc.Index(index_name)




def recipe_to_vector(recipe: Dict) -> List[float]:
    
    # ingredients 필드의 키만 사용하여 문자열로 변환
    ingredients_keys = " ".join(recipe['ingredients'].keys()) if 'ingredients' in recipe and isinstance(recipe['ingredients'], dict) else ""
            
   # 모든 값을 하나의 문자열로 연결
    text = f"{recipe.get('title', '')} {recipe.get('author', '')} {recipe.get('platform', '')} {ingredients_keys} {recipe.get('instructions', '')}"
    vector = text_to_vector(text)
    return vector

def text_to_vector(text:str) -> List[float]:
    # 텍스트를 백터로 변환
    response = openai.embeddings.create(
        input=[text],
        model= embed_model   # openAI 모델
    )
    embedding = response.data[0].embedding
    
    return embedding

# 배치 처리함수 : 백터 데이터를 100 사이즈로 나누어 업로드 (크기가 크기때문에 저장이 안되어서 나눔)
def batch_upsert(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i+batch_size]
        index.upsert(vectors=batch)
        logging.info(f'Upserted batch of size: {len(batch)}')
        
        
###  파인콘에서 백터 검색 
def search_pinecone(query: str, top_k: int = 10) -> List[Dict]:
    
    # 검색에 사용할 다른 모델
    search_model = embed_model
    response = openai.embeddings.create(
        input=[query],
        model= search_model
    )
    vector = response.data[0].embedding
    
    response = index.query(vector=[vector], top_k=top_k, include_metadata=True)
    return [match['metadata'] for match in response['matches']]
        
        
        
def compute_similarity(expected: Dict, actual: Dict) -> float:
    expected_vector = text_to_vector(f"{expected['title']} {expected['author']} {expected['ingredients']} {expected['instructions']}")
    actual_vector = text_to_vector(f"{actual['title']} {actual['author']} {actual['ingredients']} {actual['instructions']}")
    similarity = np.dot(expected_vector, actual_vector) / (np.linalg.norm(expected_vector) * np.linalg.norm(actual_vector))
    return similarity