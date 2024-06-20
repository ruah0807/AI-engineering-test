from fastapi import FastAPI, Request, Form, Query
from typing import List, Dict
from recipies import RecipeCrawler # crawling 모듈을 import


app = FastAPI()



@app.get('/')
async def home(request: Request):
    return { 'message': 'success' }

@app.get("/recipes", response_model=List[Dict])
def get_recipes(page_num: int = Query(1, description="Page number to crawl recipes from")):
    base_url = 'https://chef-choice.tistory.com'
    crawler = RecipeCrawler(base_url)
    all_recipes_data = crawler.crawling(page_num)
    return all_recipes_data