
# 필요한 라이브러리 설치
# !pip install food2vec pinecone-client

from food2vec.semantic_nutrition import Estimator
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone


# Food2Vec 초기화
estimator = Estimator()

# Pinecone 초기화
pc = Pinecone(api_key='db31f186-85fc-4d80-a8f7-45b3c4488b1b')

index_name = 'recipe-embeddings'

# 기존 인덱스 삭제 (예외 처리 추가)
try:
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
except Exception as e:
    print(f"Error deleting index: {str(e)}")


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
    response = index.upsert(vectors=[(recipe_id, embedding)])
    print(f"Upsert response for {recipe_id}: {response}")

    
#     # 샘플 임베딩 벡터의 차원 확인
# sample_embedding = estimator.embed('apple pie with cinnamon and sugar').tolist()
# print(f"Sample embedding dimension: {len(sample_embedding)}")
    
# 샘플 임베딩 벡터의 차원 확인
sample_embedding = estimator.embed('apple pie with cinnamon and sugar').tolist()
print(f"Sample embedding dimension: {len(sample_embedding)}")


# 저장된 벡터 조회
fetched_vector = index.fetch(ids=['recipe1', 'recipe2', 'recipe3'])
print("Fetched Vectors:", fetched_vector)

# 유사도 검색 함수
def find_similar_recipes(query):
    query_embedding = estimator.embed(query).tolist()
    print("Query Embedding Length:", len(query_embedding))
    print("Query Embedding:", query_embedding)  # 쿼리 벡터 확인
    
    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
    print("Query Results:", results)  # 전체 쿼리 결과 확인
    
    if results and results.get('matches'):
        for match in results['matches']:
            print(f"ID: {match['id']}, Score: {match['score']}")
    else:
        print("No matches found.")
    
    return results.get('matches', [])

# print(f"Vector for 'apple pie with cinnamon and sugar': {estimator.embed('apple pie with cinnamon and sugar')}")

# 예제 사용
query_text = 'apple dessert'
similar_recipes = find_similar_recipes(query_text)
print("Similar Recipes:", similar_recipes)


