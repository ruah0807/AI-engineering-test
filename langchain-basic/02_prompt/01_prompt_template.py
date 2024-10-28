from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
# API KEY를 환경변수로 관리하기 위한 설정파일
from dotenv import load_dotenv

# API 정보 로드
load_dotenv()

# LangSmith 추적을 설정합니다. https://smith.langchain.com
# .env 파일에 LANGCHAIN_API_KEY를 입력합니다.
from langchain_teddynote import logging

# 프로젝트 이름을 입력합니다.
logging.langsmith("langchain_test")



from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

####################################################################

### Prompt Template 를 사용하는 방법

#### 방법 1. from_template() 메소드를 이용하여 PromptTemplate 객체 생성
# - 치환될 변수를 {변수} 로 묶어 템플릿 정의

from langchain_core.prompts import PromptTemplate 

# template 정의 . {country}는 변수로, 이후에 값이 들어갈 자리를 의미
template = "{country}의 수도는 어디인가요?"

# from_template 메소드를 이용하여 PromptTemplate 객체 생성
prompt = PromptTemplate.from_template(template)

# prompt 생성 : Format 메소드를 이용하여 변수에 값을 넣어줌.
prompt = prompt.format(country= "대한민국")

# print(prompt)

####################################################################

# template 정의 . {country}는 변수로, 이후에 값이 들어갈 자리를 의미
template = "{country}의 수도는 어디인가요?"

# from_template 메소드를 이용하여 PromptTemplate 객체 생성
prompt = PromptTemplate.from_template(template)

chain = prompt | llm 

print(chain.invoke("미국").content)