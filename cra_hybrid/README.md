MongoDB 초기 웹사이트 설정할 때 'Driver' connect.

conda create -n ace_final_test python=3.12
conda activate ace_final_test
pip install fastapi uvicorn beautifulsoup4 requests lxml fake_useragent python-dotenv "pymongo[srv]"
cd [해당폴더]
uvicorn main:app --reload --port=[포트번호]



# retrieval 플러그인 Haystack 설치

pip install farm-haystack[elasticsearch]

# 같은 경로 안에 Dockerfile 만들기

# requierements.txt 만들기

### Docker 이미지 빌드 및 컨테이너 실행

# cd /path/to/your/project # Dockerfile이 있는 디렉토리로 이동

docker build -t myfastapiapp .

# Elasticsearch 컨테이너 실행

docker run -d -p 9200:9200 -e "discovery.type=single-node" --name elasticsearch elasticsearch:7.9.2

# FastAPI 애플리케이션 컨테이너 실행

docker run -d -p 8000:8000 --name myfastapiapp --link elasticsearch:elasticsearch myfastapiapp

#
