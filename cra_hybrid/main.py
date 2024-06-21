from fastapi import FastAPI, HTTPException,Query
from typing import List, Dict

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from recipies import RecipeCrawler

# env 관련
from dotenv import load_dotenv
import os

# db예제
from pymongo.errors import BulkWriteError
from pymongo.mongo_client import MongoClient
from pymongo import UpdateOne

from pinecone import Pinecone, ServerlessSpec
from food2vec.semantic_nutrition import Estimator



# .env 파일의 변수를 프로그램 환경변수에 추가
load_dotenv()

DB_ID = os.getenv('DB_ID')
DB_PW = os.getenv('DB_PW')
DB_URL = os.getenv('DB_URL')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

app = FastAPI()

# MongoDB client 생성
uri = f'mongodb+srv://{DB_ID}:{DB_PW}{DB_URL}'
client = MongoClient(uri)
db = client.crawling_test

# Pinecone 초기화
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'recipes'
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=300,  #300 차원 백터 사용
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
index = pc.Index(index_name)


# Food2Vec 모델 로드
estimator = Estimator()


# 텍스트 임배딩 생성 함수
def embed_text(text: str) -> list:
    return estimator.embed(text).tolist()












def recipes_serializer(recipe) -> dict:
    return {
        "id" : str(recipe["_id"]),
        "recipe_id": recipe["recipe_id"] if recipe.get('recipe_id') else '',
        "title": recipe["title"] if recipe.get('title') else '',
        "oriUrl": recipe["oriUrl"] if recipe.get('oriUrl') else '',
        "level": recipe["level"] if recipe.get('level') else '',
        "serving": recipe["serving"] if recipe.get('serving') else '',
        "cookingTime": recipe["cookingTime"] if recipe.get('cookingTime') else '',
        "ingredients": recipe["ingredients"] if recipe.get('ingredients') else '',
        "instructions": recipe["instructions"] if recipe.get('instructions') else '',
        "tools": recipe["tools"] if recipe.get('tools') else '',
        "platform": recipe["platform"] if recipe.get('platform') else '',
        "publishDate": recipe["publishDate"] if recipe.get('publishDate') else '',
        "createdDate": recipe["createdDate"] if recipe.get('createdDate') else '',
        "imgUrl": recipe["imgUrl"] if recipe.get('imgUrl') else ''  
    }


## 페이지별 크롤링 확인 GET ##
@app.get("/ddook_recipes/{recipe_id}", response_model=Dict)
def get_detail_by_recipe_id(recipe_id:str):
    recipe = db.recipes.find_one({'recipe_id': recipe_id})
    if recipe : 
        return recipes_serializer(recipe)
    else:
        raise  HTTPException(status_code=404, detail='해당 번호의 뚝딱이형 레시피없음')




### 전체 크롤링 디비 저장 ###
@app.post("/ddook_recipes/save", response_model=List[Dict])
def save_recipes():
    base_url = 'https://chef-choice.tistory.com'
    crawler = RecipeCrawler(base_url)
    all_recipes_data = crawler.all_crawling()
    
    operations = [ 
                  UpdateOne({'recipe_id':recipe['recipe_id']}, {'$set': recipe}, upsert=True)
                  for recipe in all_recipes_data
                  ]
    
    if operations :
        try:
            db.recipes.bulk_write(operations)
        except BulkWriteError as bwe:
            raise HTTPException(status_code=500, detail=f'중복 레시피 에러 : {bwe.details}')
        
        
    # 저장된 레시피들만 반환
    saved_recipes_ids = [recipe['recipe_id'] for recipe in all_recipes_data]
    saved_recipes =  db.recipes.find({'recipe_id' : {'$in': saved_recipes_ids}})
        
    return [recipes_serializer(recipe) for recipe in saved_recipes]
    
    



### 페이지별 크롤링 저장 ###
@app.post("/ddook_recipes/save", response_model=List[Dict])
def save_recipes(page_num : int = Query(1, description="Page number to crawl recipes from")):
    base_url = 'https://chef-choice.tistory.com'
    crawler = RecipeCrawler(base_url)
    all_recipes_data = crawler.page_crawling(page_num)
    
    operations = [ 
                  UpdateOne({'recipe_id':recipe['recipe_id']}, {'$set': recipe}, upsert=True)
                  for recipe in all_recipes_data
                  ]
    
    if operations :
        try:
            db.recipes.bulk_write(operations)
        except BulkWriteError as bwe:
            raise HTTPException(status_code=500, detail=f'중복 레시피 에러 : {bwe.details}')
        
        
    # 저장된 레시피들만 반환
    saved_recipes_ids = [recipe['recipe_id'] for recipe in all_recipes_data]
    saved_recipes =  db.recipes.find({'recipe_id' : {'$in': saved_recipes_ids}})
        
    return [recipes_serializer(recipe) for recipe in saved_recipes]





# 하이브리드 검색 GET
@app.get('/ddook_recipes/search', response_model=List[Dict])
def search_recipes(query: str = Query(..., description='비슷한 레시피 검색')):
    embedding = embed_text(query)
    search_results = index.query(embedding, top_k=10, include_metadata=True)

    recipe_ids = [result['id'] for result in search_results['matches']]
    recipes = db.recipes.find({'recipe_id': {'$in':recipe_ids}})
    
    return [recipes_serializer(recipe) for recipe in recipes]