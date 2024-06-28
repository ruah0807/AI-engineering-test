from pymongo import MongoClient
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()
DB_URI= os.getenv('MONGODB_URI')

# MongoDB client 생성
client = MongoClient(DB_URI)
db = client['crawling_test']
collection = db['recipes']


documents = list(collection.find({}, 
                                 {
                                     '_id': 1, 
                                  'title': 1, 
                                  'ingredients': 1, 
                                  'instructions': 1
                                  }))

# 문서의 내용을 추출하고 토큰화
# 필요한 필드를 결합하여 텍스트 데이터 생성
document_texts = [
    f"{doc.get('title', '')} {' '.join(doc.get('ingredients', {}).keys())} {' '.join(doc.get('instructions', []))}"
    for doc in documents
]
tokenized_documents = [text.split() for text in document_texts]

bm25 = BM25Okapi(tokenized_documents)


def get_bm25_scores(query):
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    return scores, documents