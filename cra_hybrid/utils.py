import re
from bs4 import BeautifulSoup
from typing import Dict, List

class RecipeScraper :
    def __init__(self, soup : BeautifulSoup):
        self.soup = soup
        
        
    ### 비정형화 문서 추출 : 재료, 레시피본문 ###
    def extract_ingreidents_and_instructions(self) ->  Dict[str, List[str]]:
      
        ingredients = self.extract_ingredients()
        instructions = self.extract_instructions()
       
        return {'ingredients' : ingredients, 'instructions': instructions}


    
    ### 조리과정(레시피) 앞의 숫자, 점, 공백을 제거하는 정규 표현식 ###
    def extract_instructions(self) -> List[str]:
        ### 조리 과정 추출 ###
        instruction_tags = self.soup.find_all('p', {'data-ke-size': 'size16'})
        instructions = []
        for tag in instruction_tags:
            text = tag.get_text(strip=True)
            if text : 
                # 숫자와 닫는 괄호를 하이픈으로 대체
                text = re.sub(r'^\d+\.\s*', '', text)
                text = re.sub(r'\d+\s*\)', '-', text)
                instructions.append(text)
        return instructions
    
    
    
    ### 재료 예외처리 ###
    def extract_ingredients(self) -> Dict[str, str]:
        ingredients = {}
        p_tags = self.soup.find_all('p', style="text-align: center;")
        temp_ingredients = []
        for p_tag in p_tags:
            span_texts = [span.get_text(strip=True) for span in p_tag.find_all('span') if span.get_text(strip=True)]
            if span_texts:
                temp_ingredients.append(' '.join(span_texts))

        temp_ingredients = [item for item in temp_ingredients if '재료' not in item]
        invalid_entry = False
        for item in temp_ingredients:
            item = item.replace('[재료]', '').replace('(', '').replace(')', '').strip()
            if '<' in item or '>' in item:
                invalid_entry = True
                break
            if ':' in item:
                name, amount = item.split(':', 1)
                ingredients[name.strip()] = amount.strip()
            else:
                ingredients[item.strip()] = ''

        if invalid_entry or not ingredients:
            blockquote_tag = self.soup.find('blockquote')
            if blockquote_tag:
                ingredients_list = blockquote_tag.get_text(separator="\n").strip().split('\n')
                for item in ingredients_list:
                    item = item.replace('[재료]', '').replace('(', '').replace(')', '').strip()
                    if '재료' not in item:
                        if ':' in item:
                            name, amount = item.split(':', 1)
                            ingredients[name.strip()] = amount.strip()
                        else:
                            ingredients[item.strip()] = ''

        ingredients = {k: v for k, v in ingredients.items() if k}
        return ingredients