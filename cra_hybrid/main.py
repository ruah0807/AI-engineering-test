from fastapi import FastAPI, HTTPException,Query
from typing import List, Dict

from bs4 import BeautifulSoup
import numpy as np
from fake_useragent import UserAgent

from recipies import RecipeCrawler
from vector.recipe2vec import recipe_to_vector, batch_upsert, search_pinecone, compute_similarity
from vector.test_elastic import search_elasticsearch


# env 관련
from dotenv import load_dotenv
import os

# db예제
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError
from pymongo.mongo_client import MongoClient
from pymongo import UpdateOne
import logging
import json

app = FastAPI()

# .env 파일의 변수를 프로그램 환경변수에 추가
load_dotenv()


DB_URI= os.getenv('MONGODB_URI')


# MongoDB client 생성
client = MongoClient(DB_URI)
db = client['ace_final_test']
collection = db['recipes']
    
logging.basicConfig(level=logging.INFO)

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
@app.post("/ddook_recipes/save_all", response_model=List[Dict])
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




  
  

## 백터(values):
#	•	백터는 숫자들의 긴 리스트입니다. 이 숫자들은 컴퓨터가 텍스트나 이미지 같은 정보를 이해하고 비교할 수 있게 해줍니다.
#	•	예를 들어, 레시피 제목, 작성자, 재료, 조리 방법 같은 텍스트를 긴 숫자 리스트로 변환합니다. 
#       이 리스트는 컴퓨터가 유사한 레시피를 빠르게 찾을 수 있게 도와줍니다.

### 	메타데이터(metadata):
#	•	메타데이터는 레시피에 대한 추가 정보를 담고 있습니다. 여기에는 레시피의 제목, 작성자, 이미지 URL, 
#       게시 날짜 같은 것들이 포함됩니다.
#	•	이 정보는 사람이 읽을 수 있게 되어 있어서, 검색 결과를 사용자에게 보여줄 때 사용합니다.


### 몽고DB에 저장된 데이터 파인콘에 백터화한 후 저장 ###
@app.post('/ddook_recipes/index_to_pinecone', response_model=Dict)
def index_to_pinecone():
    
    try:
        recipes = collection.find()
        vectors = []        
        existing_ids = set()
        
        for count, recipe in enumerate(recipes, start=1):
            try:
                if str(recipe['_id']) in existing_ids:
                    logging.warning(f"Skipping duplicate recipe with id: {recipe['_id']}")
                    continue
                vector = {
                    'id': str(recipe['_id']),
                    'values': recipe_to_vector(recipe),
                    'metadata': {
                        'title': recipe.get('title', ''),
                        'author': recipe.get('author', ''),
                        'platform': recipe.get('platform', ''),
                        'imgUrl': recipe.get('imgUrl', ''),
                        'publishDate': recipe.get('publishDate', '')
                    }
                }
                vectors.append(vector)
                existing_ids.add(str(recipe['_id']))
                
                if count % 100 == 0:
                    logging.info(f'Processed {count} recipes')
                    
                if count % 1000 == 0:
                    batch_upsert(vectors)
                    vectors = []  # 벡터 리스트 초기화
            
            except Exception as e:
                logging.error(f"Error processing recipe with id: {recipe['_id']} - {str(e)}")
            
        if vectors:  # 마지막 배치를 업로드
            batch_upsert(vectors)
        logging.info('All vectors upserted successfully')
        return {'status': 'success', 'indexed': len(vectors)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get('/search_recipes', response_model=List[Dict])
def search_recipes(query: str):
    try:
        # 파인콘에서 벡터 검색
        metadata_list = search_pinecone(query)
        if not metadata_list:
            return []
        return metadata_list
        
        # 엘라스틱서치에서 문서 검색
        documents = search_elasticsearch(metadata_list)
        if not documents:
            return []
        
        # 파인콘과 엘라스틱서치 결과 통합
        final_results = []
        for metadata in metadata_list:
            for doc in documents:
                if metadata['title'] == doc['title'] and metadata['author'] == doc['author']:
                    final_results.append({
                        'title': metadata['title'],
                        'author': metadata['author'],
                        'imgUrl': metadata['imgUrl'],
                        'publishDate': metadata['publishDate'],
                        # 'instructions': doc['instructions'],
                        # 'ingredients': doc['ingredients']
                    })
                    break
        
        return final_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get ('/evaluate_search', response_model=Dict[str, float])
def evaluate_search(query: str):
    try:
        metadata_list = search_pinecone(query)
        if not metadata_list :
            return {'accuracy': 0}
        
        # 예시 expected 데이터 (실제 데이터와 비교할 용도로 사용)
        expected = {
            'title': '케이크',
            'author': '홍길동',
            'ingredients': '밀가루, 설탕, 계란',
            'instructions': '혼합 후 굽기'
        }

        # 상위 5개의 검색 결과에 대해 유사도 계산
        similarities = [compute_similarity(expected, result) for result in metadata_list[:5]]
        accuracy = np.mean(similarities) * 10  # 0 ~ 10 점수로 환산
        
        return {"accuracy": accuracy}
    except Exception as e :
        raise HTTPException (status_code=500, detail = str(e))