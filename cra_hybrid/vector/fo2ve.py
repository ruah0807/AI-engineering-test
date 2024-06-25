from sentence_transformers import SentenceTransformer
from typing import List,Dict
from food2vec.semantic_nutrition import Estimator
import numpy as np

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
food2vec = Estimator()

def recipe_to_vector_food2vec(recipe: Dict) -> List[float]:

    # food2vec 임베딩 벡터 리스트 초기화
    ingredient_vectors = []
    
    for ingredient in recipe['ingredients']:
        try:
            vector = food2vec.embed(ingredient)
            if vector is not None:
                ingredient_vectors.append(vector)
            else:
                print(f"Embedding for '{ingredient}' returned None.")
        except ValueError as e:
            # 단어가 모델에 없거나 임베딩 중 오류 발생 시 무시
            print(f"Embedding error for ingredient '{ingredient}': {e}")
            continue
    
    # 재료 벡터들의 평균을 구하여 최종 벡터 생성
    if ingredient_vectors:
        ingredients_vector = np.mean(ingredient_vectors, axis=0)
    else:
        # food2vec 임베딩 실패 시 기본 벡터 사용
        ingredients_vector = np.zeros(food2vec.embed('water').shape)
    
    # 번역된 재료를 하나의 문자열로 연결 (title, author, instructions 포함)
    text = f"{recipe['title']} {recipe['author']} {recipe['instructions']}"
    
    # 나머지 텍스트를 임베딩하여 벡터 생성
    text_vector = some_embedding_function_food2vec(text)
    
    # 재료 벡터와 나머지 텍스트 벡터를 결합
    final_vector = np.concatenate((ingredients_vector, text_vector))
    return final_vector.tolist()






def some_embedding_function_food2vec(text:str) -> List[float]:
    # 텍스트를 백터로 변환
    embedding = model.encode(text)
    return embedding.tolist()
    