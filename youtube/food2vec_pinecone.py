
# 필요한 라이브러리 설치
# !pip install food2vec pinecone-client

from food2vec.semantic_nutrition import Estimator
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone


import pinecone

# Food2Vec 초기화
estimator = Estimator()

# Pinecone 초기화
pc = Pinecone(api_key='db31f186-85fc-4d80-a8f7-45b3c4488b1b')

index_name = 'recipe-embeddings'

# 인덱스 생성 (존재하지 않을 경우에만)
if index_name not in pc.list_indexes():
    pc.create_index(
        name=index_name, 
        dimension=300, 
        metric='cosine', 
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
    ))
    

index = pc.Index(index_name)

# 샘플 레시피 데이터
recipes = {
    'recipe1': 'apple pie with cinnamon and sugar',
    'recipe2': 'banana bread with walnuts',
    'recipe3': 'grilled chicken with herbs'
}

# 레시피 임베딩 생성 및 삽입
for recipe_id, recipe_text in recipes.items():
    embedding = estimator.embed(recipe_text).tolist()
    index.upsert(vectors=[(recipe_id, embedding)])

print(embedding)

# 유사도 검색 함수
def find_similar_recipes(query):
    query_embedding = estimator.embed(query).tolist()
    results = index.query(vector=query_embedding, top_k=5, include_values=True)
    return results['matches']

# 예제 사용
query_text = 'apple dessert'
similar_recipes = find_similar_recipes(query_text)
print(similar_recipes)
