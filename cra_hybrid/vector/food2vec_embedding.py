from food2vec.semantic_nutrition import Estimator
import numpy as np
from typing import List,Dict
import json


model = Estimator()

def recipe_to_vector_food2vec(recipe:Dict)-> List[float]:
    # 레시피의 재료를 벡터로 변환하는 로직
    ingredients = json.dumps(recipe["ingredients"], ensure_ascii=False)
    vector = some_embedding_function_food2vec(ingredients)
    return vector

def some_embedding_function_food2vec(text:str) -> List[float]:
    # 텍스트를 백터로 변환
    embedding = model.encode(text)[0]
    return embedding.tolist()