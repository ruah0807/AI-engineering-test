from fastapi import FastAPI, Request, Form, Query
from typing import List, Dict
from recipies import crawling # crawling 모듈을 import


app = FastAPI()



@app.get('/')
async def home(request: Request):
    return { 'message': 'success' }

@app.get("/recipes", response_model=List[Dict])
def get_recipes(page_num: int = Query(1, description="Page number to crawl recipes from")):
    base_url = 'https://chef-choice.tistory.com'
    all_recipes_data = crawling(base_url, page_num)
    return all_recipes_data