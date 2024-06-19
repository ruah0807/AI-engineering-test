import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import concurrent.futures

def get_page_url(base_url:str, page_num:int) -> str :
    '''주어진 페이지 번호에 해당하는 url을 반환'''
    return f'{base_url}?page={page_num}' if page_num > 1 else base_url

def crawl_page(url: str) -> List[str]:
    """주어진 URL에 대해 레시피를 크롤링하고, 각 레시피 링크를 추출합니다."""
    data = requests.get(url)
    soup = BeautifulSoup(data.content, 'html.parser')
    
       # 두 번째 스크린샷에서 나온 링크만 선택
    links = soup.select('#content_article_rep .link_thumb')
    recipe_links = [f'https://chef-choice.tistory.com{link.get("href")}' for link in links if link.get("href")]
    
    return recipe_links


def extract_ingreidents_and_instructions(soup:BeautifulSoup) ->  Dict[str, List[str]]:
    # 재료 추출
    ingredients = {}
    

    # p 태그 먼저 확인
    p_tags = soup.find_all('p', style="text-align: center;")
    temp_ingredients = []
    for p_tag in p_tags:
        span_texts = [span.get_text(strip=True) for span in p_tag.find_all('span') if span.get_text(strip=True)]
        if span_texts:
            temp_ingredients.append(' '.join(span_texts))

    # '재료'라는 단어가 포함된 항목 제거
    temp_ingredients = [item for item in temp_ingredients if '재료' not in item]
    invalid_entry = False
    for item in temp_ingredients:
        item = item.replace('[재료]', '').replace('(', '').replace(')', '').strip()  # 대괄호와 소괄호 제거
        if '<' in item or '>' in item:  # '<' 또는 '>'가 포함된 항목은 예외 처리
            invalid_entry = True
            break
        if ':' in item:
            name, amount = item.split(':', 1)  # 첫 번째 콜론을 기준으로 분리
            ingredients[name.strip()] = amount.strip()
        else:
            ingredients[item.strip()] = ''  # 콜론이 없는 항목 처리

    # blockquote 태그 확인 (p 태그에서 재료를 찾지 못한 경우)
    if invalid_entry or not ingredients:
        blockquote_tag = soup.find('blockquote')
        if blockquote_tag:
            ingredients_list = blockquote_tag.get_text(separator="\n").strip().split('\n')
            for item in ingredients_list:
                item = item.replace('[재료]', '').replace('(', '').replace(')', '').strip()  # 대괄호와 소괄호 제거
                if '재료' not in item:  # '재료'가 포함되지 않은 항목만 처리
                    if ':' in item:
                        name, amount = item.split(':', 1)  # 첫 번째 콜론을 기준으로 분리
                        ingredients[name.strip()] = amount.strip()
                    else:
                        ingredients[item.strip()] = ''  # 콜론이 없는 항목 처리

    # 빈 키 제거
    ingredients = {k: v for k, v in ingredients.items() if k}
    
   # 조리 과정 추출
    instruction_tags = soup.find_all('p', {'data-ke-size': 'size16'})
    instructions = [tag.get_text(strip=True) for tag in instruction_tags if tag.get_text(strip=True)]

    return {'ingredients' : ingredients, 'instructions': instructions}



def get_recipe_detail(recipe_url:str)->Dict:
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
    details = extract_ingreidents_and_instructions(soup)
    
    #recipe_id 추출
    recipe_id = recipe_url.split('/')[-1]
    
       
                
    return {
        'recipe_id' : recipe_id,
        'oriUrl' : recipe_url,
        'author' : '뚝딱이형',
        'serving' : '약 1~2인분',
        'cookingTime': '약 30분 이내',
        'level' : '초~중급',
        'title' : title,
        'date' : date,
        'imgUrl' : img_url,
        'ingredients' : details['ingredients'],
        'tools' : '정보 없음',
        'instructions' : details['instructions']
    }



def crawling(base_url: str, page_num: int)-> List[Dict]:
    url = get_page_url(base_url, page_num)
    
    page_recipes = crawl_page(url)
                
    if not page_recipes:
        return []
    
        # 크롤링 속도를 높이기 위한 함수
    with concurrent.futures.ThreadPoolExecutor() as executor:
        recipe_details = list(executor.map(get_recipe_detail, page_recipes))
    
    print(f"수집된 레시피 데이터 개수: {len(recipe_details)}")
    return list(recipe_details)
        


# # 함수 호출 예시
# crawling()