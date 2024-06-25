from elasticsearch import Elasticsearch, helpers
import numpy as np
from typing import List,Dict
from dotenv import load_dotenv
from bson import ObjectId
import json
import os

load_dotenv()

from pymongo.mongo_client import MongoClient
DB_URI= os.getenv('MONGODB_URI')

# MongoDB client 생성
client = MongoClient(DB_URI)
db = client['ace_final_test']
collection = db['recipes']

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

# 인덱스 이름 설정
index_name = 'recipes_elastics'


# NumPy 데이터 타입을 기본 Python 데이터 타입으로 변환하는 함수
def convert_numpy_types(data):
    if isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(element) for element in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (np.float32, np.float64)):
        return float(data)
    elif isinstance(data, (np.int32, np.int64)):
        return int(data)
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

# MongoDB에서 데이터 조회
def fetch_data_from_mongo():
    documents = list(collection.find())
    return [convert_numpy_types(doc) for doc in documents]

# 인덱스 삭제
def delete_index(index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted.")

# 인덱스 생성 (필드 수 제한 설정 포함)
def create_index_with_settings(index_name, max_fields=2000):
    settings = {
        "settings": {
            "index.mapping.total_fields.limit": max_fields
        }
    }
    es.indices.create(index=index_name, body=settings)
    print(f"Index '{index_name}' created with max_fields={max_fields}.")
        

# ElasticSearch에 데이터 인덱싱
def index_data_to_elasticsearch(documents, index_name):
    actions = []
    for doc in documents:
        # _id 필드를 제거하고 별도로 저장
        doc_id = str(doc.pop('_id'))
        action = {
            "_index": index_name,
            "_id": doc_id,
            "_source": doc
        }
        actions.append(action)
    success, failed = helpers.bulk(es, actions, stats_only=True)
    print(f"Successfully indexed {success} documents, failed to index {failed} documents.")


# 실행
index_name = 'recipes_elastics'
delete_index(index_name)
create_index_with_settings(index_name)
documents = fetch_data_from_mongo()
index_data_to_elasticsearch(documents, index_name)
print(f"Fetched and indexed {len(documents)} documents to ElasticSearch.")


# # ElasticSearch에 저장된 문서 수 확인 함수
# def count_documents(index_name):
#     count = es.count(index=index_name)
#     return count['count']

# # 문서 수 확인
# document_count = count_documents(index_name)
# print(f"Total documents in '{index_name}': {document_count}")



# def search_elasticsearch(metadata_list) -> List[Dict]:
    
#     should_clauses = []  # 검색 조건을 저장할 리스트
    
#     # 메타데이터 리스트를 순회하며 검색 조건을 생성
#     for metadata in metadata_list:
#         # 제목, 작성자로 검색 조건 추가
#         should_clauses.append({
#             'match': {
#                 'title': metadata['title']
#             }
#         })
#         should_clauses.append({
#             'match': {
#                 'author': metadata['author']
#             }
#         })
       
#     # 검색 쿼리 생성 
#     query_body = {
#         'query': {
#             'bool' :{
#                 'should' : should_clauses   # "OR" 조건으로 검색 조건들을 추가
#             }
#         }
#     }
#     # 엘라스틱서치에 검색 요청
#     response = es.search(index='recipes', body=query_body)
#     # 필요한 필드만 반환
#     documents = [
#         {
#             'title': hit['_source']['title'],
#             'author': hit['_source']['author'],
#             'imgUrl': hit['_source']['imgUrl'],
#             'publishDate': hit['_source']['publishDate']
#         }
#         for hit in response['hits']['hits']
#     ]
#     return documents