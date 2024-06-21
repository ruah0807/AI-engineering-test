from sentence_transformers import SentenceTransformer
from typing import List,Dict




# 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def recipe_to_vector(recipe:Dict)-> List[float]:
    # 레시피를 백터로 변환하는 로직
    # 예시로 모든 값을 하나의 문자열로 연결, 그 문자열을 임베딩하여 백터를 생성하는 방식 사용
    text = f'{recipe['title']}{recipe['author']}{recipe['ingredients']}{recipe['instructions']}'
    vector = some_embedding_function(text)
    return vector

def some_embedding_function(text:str) -> List[float]:
    # 텍스트를 백터로 변환
    embedding = model.encode(text)
    return embedding.tolist()
    
