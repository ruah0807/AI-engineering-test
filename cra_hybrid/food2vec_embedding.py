from food2vec.semantic_nutrition import Estimator
import numpy as np

model = Estimator()

def embed_text(text:str )-> str:
    return model.embed(text)    
    
text = 'spaghetti carbonara'
embedding = embed_text(text)
print(embedding)
    