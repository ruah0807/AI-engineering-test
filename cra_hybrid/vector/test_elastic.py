from elasticsearch import Elasticsearch
from typing import List,Dict
from dotenv import load_dotenv
import json
import os

load_dotenv()

from pymongo.mongo_client import MongoClient
DB_URI= os.getenv('MONGODB_URI')

# MongoDB client 생성
client = MongoClient(DB_URI)
db = client['crawling_test']
collection = db['recipes']

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

# if es.indices.exists(index='recipes'):
#     es.indices.delete(index='recipes')

# # 엘라스틱 데이터 저장 
# else:
   
#     # 인덱스 생성 및 매핑 설정
#     settings = {
#         "settings": {
#             "index": {
#                 "mapping": {
#                     "total_fields": {
#                         "limit": "2000"  # 필드 수 제한 설정
#                     }
#                 }
#             }
#         },
#         "mappings": {
#             "properties": {
#                 "title": {"type": "text"},
#                 "author": {"type": "text"},
#                 "ingredients": {"type": "text"},  # 문자열로 처리
#                 "instructions": {"type": "text"},
#                 "imgUrl": {"type": "text"},
#                 "publishDate": {"type": "date"}
#             }
#         }
#     }

#     es.indices.create(index='recipes', body=settings) 
    
    
# def index_data_to_elasticsearch():
#     recipes = collection.find()
#     for recipe in recipes:
#         document = {
#             'title': recipe['title'],
#             'author': recipe['author'],
#             'ingredients': recipe['ingredients'],
#             'instructions': recipe['instructions'],
#             'imgUrl': recipe['imgUrl'],
#             'publishDate': recipe['publishDate']
#         }
#         es.index(index='recipes', id=str(recipe['_id']), document=document)

# index_data_to_elasticsearch()


def search_elasticsearch(metadata_list) -> List[Dict]:
    
    should_clauses = []  # 검색 조건을 저장할 리스트
    
    # 메타데이터 리스트를 순회하며 검색 조건을 생성
    for metadata in metadata_list:
        # 제목, 작성자로 검색 조건 추가
        should_clauses.append({
            'match': {
                'title': metadata['title']
            }
        })
        should_clauses.append({
            'match': {
                'author': metadata['author']
            }
        })
       
    # 검색 쿼리 생성 
    query_body = {
        'query': {
            'bool' :{
                'should' : should_clauses   # "OR" 조건으로 검색 조건들을 추가
            }
        }
    }
    # 엘라스틱서치에 검색 요청
    response = es.search(index='recipes', body=query_body)
    # 필요한 필드만 반환
    documents = [
        {
            'title': hit['_source']['title'],
            'author': hit['_source']['author'],
            'imgUrl': hit['_source']['imgUrl'],
            'publishDate': hit['_source']['publishDate']
        }
        for hit in response['hits']['hits']
    ]
    return documents