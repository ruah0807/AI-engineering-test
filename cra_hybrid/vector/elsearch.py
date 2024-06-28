from elasticsearch import Elasticsearch
from typing import List, Dict,Tuple
from dotenv import load_dotenv
from bson import ObjectId
import json
import os

load_dotenv()

from pymongo.mongo_client import MongoClient
DB_URI = os.getenv('MONGODB_URI')

# MongoDB client 생성
client = MongoClient(DB_URI)
db = client['crawling_test']
collection = db['recipes']

# MongoDB에서 데이터 가져오기
documents = list(collection.find())

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

# 인덱스 이름 설정
index_name = 'recipes_elastics'

# # ObjectId를 문자열로 변환하는 함수
# def convert_object_id(doc):
#     if '_id' in doc and isinstance(doc['_id'], ObjectId):
#         doc['_id'] = str(doc['_id'])
#     return doc

# # ingredients 필드를 문자열로 변환하는 함수
# def convert_ingredients_to_str(doc):
#     if 'ingredients' in doc and isinstance(doc['ingredients'], dict):
#         doc['ingredients'] = json.dumps(doc['ingredients'], ensure_ascii=False)
#     return doc


# # 인덱스 생성 및 설정 변경
# settings = {
#     "settings": {
#         "index.mapping.total_fields.limit": 2000  # 필드 수 제한 증가
#     }
# }

# es.indices.create(index=index_name, body=settings)


# # 데이터 인덱싱
# for document in documents:
#     document = convert_object_id(document)
#     document = convert_ingredients_to_str(document)
#     document_id = document.pop('_id')  # _id 필드를 문서에서 제거
#     es.index(index=index_name, id=document_id, document=document)

# print(f'Indexed {len(documents)} documents from MongoDB to Elasticsearch')

# 검색 함수

def search_elasticsearch(query: str, index_name: str) -> List[Tuple[str, float, str]]:
    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "ingredients", "instructions"]
            }
        }
    }
    response = es.search(index=index_name, body=search_body)
    results = []
    for hit in response['hits']['hits']:
        doc_id = hit['_id']
        score = hit['_score']
        title = hit['_source']['title']
        results.append((doc_id, score, title))
    return results


# # 예시 검색
# query = "김치"  # 검색어 설정
# results = search_elasticsearch(query, index_name)
# for hit in results['hits']['hits']:
#     print(f"Document ID: {hit['_id']}, Title: {hit['_source']['title']}, Score: {hit['_score']}")