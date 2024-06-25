from typing import List,Dict
import os
from dotenv import load_dotenv
from pinecone import Pinecone
import numpy as np
import logging
from transformers import AutoModel, AutoTokenizer,BertModel, BertTokenizer
import torch

# 환경 변수 로드
load_dotenv()
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# Pinecone 초기화
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'recipeskobertroberta'
index = pc.Index(index_name)


#  모델 로드
kobert_name = 'monologg/kobert'
kobert_tokenizer = BertTokenizer.from_pretrained(kobert_name)
kobert_model = BertModel.from_pretrained(kobert_name)

roberta_name = 'BM-K/KoSimCSE-roberta-multitask'
roberta_tokenizer = AutoTokenizer.from_pretrained(roberta_name)
roberta_model = AutoModel.from_pretrained(roberta_name) 


def recipe_to_vector(recipe: Dict) -> List[float]:
    
    # ingredients 필드의 키만 사용하여 문자열로 변환
    ingredients_keys = " ".join(recipe['ingredients'].keys()) if 'ingredients' in recipe and isinstance(recipe['ingredients'], dict) else ""
    platform = recipe.get('platform', '')
    author = recipe.get('author', '')
         
    # koBert : 단어 위주의 임베딩 
    kobert_text = f"{ingredients_keys} {platform} {author}"
    kobert_inputs = kobert_tokenizer(kobert_text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        kobert_outputs = kobert_model(**kobert_inputs)
    kobert_vector = kobert_outputs.pooler_output.squeeze().numpy()
    
    # roBERTa 임베딩 : 문장 위주의 임베딩
    roberta_text= f"{recipe.get('title', '')} {recipe.get('instructions', '')}"
    roberta_inputs = roberta_tokenizer(roberta_text, return_tensors='pt', padding=True, truncation=True , max_length=512)    # 
    with torch.no_grad():
        roberta_outputs = roberta_model(**roberta_inputs,  return_dict=True)
    
    roberta_vector = roberta_outputs['last_hidden_state'].mean(dim=1).squeeze().numpy()
    
    # 두 벡터 결합
    combined_vector = np.concatenate((kobert_vector, roberta_vector))

    return combined_vector.tolist()




## koBert 사용 백터 변환
def text_to_vector_kobert(text:str) -> List[float]:

    kobert_inputs = kobert_tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        kobert_outputs = kobert_model(**kobert_inputs, return_dict=True)
    kobert_vector = kobert_outputs.pooler_output.squeeze().numpy()
    
    return kobert_vector.tolist()


###  RoBERTa 사용 백터 변환 
def text_to_vector_roberta(text: str)  -> List[float]:
    
    roberta_inputs = roberta_tokenizer(text, return_tensors='pt', padding=True, truncation=True , max_length=512)     
    with torch.no_grad():
        roberta_outputs = roberta_model(**roberta_inputs,  return_dict=True)
    
    roberta_vector = roberta_outputs['last_hidden_state'].mean(dim=1).squeeze().numpy()
    
    return roberta_vector.tolist()

        
# 멀티 임베딩을 사용하여 백터 검색    
def search_pinecone(query: str, top_k : int = 10) -> List[Dict]:
    
    #koBERT 백터 생성
    kobert_vector = text_to_vector_kobert(query)
    
    #RoBERTa 벡터 생성
    roberta_vector = text_to_vector_roberta(query)
    
    # 두 벡터 결합
    combined_vector = np.concatenate((kobert_vector, roberta_vector))
    
    # Pinecone에서 검색
    response = index.query(vector=combined_vector.tolist(), top_k=top_k, include_metadata=True)
    
    return [match['metadata'] for match in response['matches']]


# 배치 처리함수 : 백터 데이터를 100 사이즈로 나누어 업로드 (크기가 크기때문에 저장이 안되어서 나눔)
def batch_upsert(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i+batch_size]
        index.upsert(vectors=batch)
        logging.info(f'Upserted batch of size: {len(batch)}')
        
        

        
def compute_similarity(expected: Dict, actual: Dict) -> float:
    expected_text = f"{expected['title']} {expected['author']} {expected['ingredients']} {expected['instructions']}"
    actual_text = f"{actual['title']} {actual['author']} {actual['ingredients']} {actual['instructions']}"
    
    # KoBERT와 RoBERTa를 사용하여 벡터 생성
    expected_vector_kobert = text_to_vector_kobert(expected_text)
    actual_vector_kobert = text_to_vector_kobert(actual_text)
    
    expected_vector_roberta = text_to_vector_roberta(expected_text)
    actual_vector_roberta = text_to_vector_roberta(actual_text)
    
    # 벡터 결합
    expected_vector = np.concatenate((expected_vector_kobert, expected_vector_roberta))
    actual_vector = np.concatenate((actual_vector_kobert, actual_vector_roberta))
    
    similarity = np.dot(expected_vector, actual_vector) / (np.linalg.norm(expected_vector) * np.linalg.norm(actual_vector))
    return similarity






