from typing import List,Dict
import openai
import os
from dotenv import load_dotenv
from pinecone import Pinecone


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


def recipe_to_vector(recipe:Dict)-> List[float]:
    # 레시피를 백터로 변환하는 로직
    # 모든 값을 하나의 문자열로 연결, 그 문자열을 임베딩하여 백터를 생성하는 방식 사용
    text = f"{recipe['title']}{recipe['author']}{recipe['ingredients']}{recipe['instructions']}"
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
        
        
###  파인콘에서 백터 검색 
def search_pinecone(query: str, top_k: int = 20) -> List[Dict]:
    
    response = openai.embeddings.create(
        input=[query],
        model=embed_model
    )
    vector = response.data[0].embedding
    
    response = index.query(vector=[vector], top_k=top_k, include_metadata=True)
    return [match['metadata'] for match in response['matches']]
        


