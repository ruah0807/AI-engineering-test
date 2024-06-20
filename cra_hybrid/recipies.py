import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import concurrent.futures
from utils import RecipeScraper
import datetime as dt



class RecipeCrawler :
    
    
    ### 초기화 ###
    def __init__(self, base_url: str):
        self.base_url = base_url
       
       
    ### 주어진 페이지 번호에 해당하는 url을 반환 ###
    def get_page_url(self, page_num:int) -> str :
        return f'{self.base_url}?page={page_num}' if page_num > 1 else self.base_url


    ### 주어진 URL에 대해 레시피를 크롤링하고, 각 레시피 링크를 추출합니다. ####
    def crawl_page(self, url: str) -> List[str]:
       
        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        
        # 두 번째 스크린샷에서 나온 링크만 선택
        links = soup.select('#content_article_rep .link_thumb')
        recipe_links = [f'https://chef-choice.tistory.com{link.get("href")}' for link in links if link.get("href")]
        
        return recipe_links



    ### 리스트 본문에서 디테일 가져오기 ###
    def get_recipe_detail(self, recipe_url:str)->Dict:
        
        data = requests.get(recipe_url)
        
        soup = BeautifulSoup(data.content, 'html.parser')
        
        try:
            title = soup.find('p', class_='txt_sub_tit').text.strip()
            date = soup.find('span', class_='date').text.strip()
            figure_tag = soup.find('figure', class_='imageblock alignCenter')
        except AttributeError as e:
            print(f"Error parsing recipe {recipe_url}: {e}")
            return {}
        
        #이미지 추출
        img_url = None
        if figure_tag:
            img_tag = figure_tag.find('img')
            img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
            
        #재료 및 조리과정 추출
        scraper = RecipeScraper(soup)
        details = scraper.extract_ingreidents_and_instructions()
        
        #recipe_id 추출
        recipe_id = recipe_url.split('/')[-1]
        
        # 현재 날짜와 시간을 yyyy-mm-dd hh:MM:ss 형식으로 저장
        created_date = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'recipe_id' : recipe_id,
            'oriUrl' : recipe_url,
            'author' : '뚝딱이형',
            'serving' : '',
            'cookingTime': '',
            'level' : '',
            'title' : title,
            'publishDate' : date,
            'createdDate' : created_date,
            'imgUrl' : img_url,
            'ingredients' : details['ingredients'],
            'tools' : '',
            'instructions' : details['instructions']
        }



    ### 페이지별 크롤링하기 ###
    def page_crawling(self, page_num: int)-> List[Dict]:
        url = self.get_page_url(page_num)
        
        page_recipes = self.crawl_page(url)
                    
        if not page_recipes:
            return []
        
            # 크롤링 속도를 높이기 위한 함수
        with concurrent.futures.ThreadPoolExecutor() as executor:
            recipe_details = list(executor.map(self.get_recipe_detail, page_recipes))
        
        print(f"수집된 레시피 데이터 개수: {len(recipe_details)}")
        return list(recipe_details)
            
            
    ### 전체 크롤링 ###
    def all_crawling(self) -> List[Dict]:
        page_num = 1
        all_recipes_data = []
        
        while True:
            url = self.get_page_url(page_num)
            page_recipes = self.crawl_page(url)
                        
            if not page_recipes:
                break
            
                # 크롤링 속도를 높이기 위한 함수
            with concurrent.futures.ThreadPoolExecutor() as executor:
                recipe_details = list(executor.map(self.get_recipe_detail, page_recipes))
                
                all_recipes_data.extend(recipe_details)
                page_num += 1
        
        print(f"전체 수집된 레시피 데이터 개수: {len(all_recipes_data)}")
        return all_recipes_data
            

