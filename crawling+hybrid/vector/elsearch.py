from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import os
from pymongo import MongoClient

# 환경 변수 로드
load_dotenv()
DB_URI = os.getenv('MONGODB_URI')

# MongoDB client 생성
client = MongoClient(DB_URI)
db = client['crawling_test']
collection = db['recipes']

# Elasticsearch client 생성
es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

# 인덱스 설정
index_name = 'recipes_elastics'
es.indices.create(index=index_name, ignore=400)

# MongoDB에서 문서 가져오기
documents = list(collection.find({}, {
    '_id': 1,
    'title': 1,
    'ingredients': 1,
    'instructions': 1
}))

# 문서의 내용을 추출하고 텍스트 데이터 생성
document_texts = [
    f"{doc.get('title', '')} {' '.join(doc.get('ingredients', {}).keys())} {' '.join(doc.get('instructions', []))}"
    for doc in documents
]

# 데이터와 BM25 점수를 Elasticsearch에 저장
actions = [
    {
        '_index': index_name,
        '_id': str(doc['_id']),
        '_source': {
            'title': doc.get('title', ''),
            'ingredients': doc.get('ingredients', {}),
            'instructions': doc.get('instructions', [])
        }
    }
    for doc in documents
]

# 데이터 인덱싱
helpers.bulk(es, actions)
print('데이터가 Elasticsearch에 저장되었습니다.')