from elasticsearch import Elasticsearch, helpers
from typing import List, Dict,Tuple
from dotenv import load_dotenv
from bson import ObjectId
from rank_bm25 import BM25Okapi
import bm25 as bm



es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

# 인덱스 설정
index_name = 'recipes_elastics'
es.indices.create(index=index_name, ignore=400)


# 데이터와 BM25 점수를 Elasticsearch에 저장
actions = [
    {
        '_index': index_name,
        '_id': str(doc['_id']),
        '_source': {
            'title': doc.get('title', ''),
            'ingredients': doc.get('ingredients', {}),
            'instructions': doc.get('instructions', []),
            'bm25_score': score
        }
    }
    for doc, score in zip(bm.documents, bm.scores)
]


# 데이터 인덱싱
helpers.bulk(es, actions)
print('bm25점수 계산 및 elasticsearch에 저장완료')


# Elasticsearch에서 검색
search_query = {
    'query': {
        'multi_match': {
            'query': bm.query,
            'fields': ['title', 'ingredients', 'instructions']
        }
    }
}
es_response = es.search(index=index_name, body= search_query)

# Elasticsearch 점수 추출
es_scores = {hit['_id']: hit['_score'] for hit in es_response['hits']['hits']}
