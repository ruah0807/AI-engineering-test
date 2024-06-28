MongoDB 초기 웹사이트 설정할 때 'Driver' connect.

conda create -n ace_final_test python=3.12
conda activate ace_final_test
pip install fastapi uvicorn beautifulsoup4 requests lxml fake_useragent python-dotenv "pymongo[srv]"
cd [해당폴더]
uvicorn main:app --reload --port=[포트번호]

# 엘라스틱서치 구현

pip install elasticsearch

# Docker 설치

https://www.docker.com/products/docker-desktop/

# 터미널에 명령어 elasticsearch 이미지 가져오기

docker pull docker.elastic.co/elasticsearch/elasticsearch:8.14.1

# 프로젝트 디렉토리에 docker-compose.yml파일 생성 후 아래 내용 추가

version: "3"
services:
elasticsearch:
image: docker.elastic.co/elasticsearch/elasticsearch:8.14.1
container_name: elasticsearch
environment: - discovery.type=single-node - xpack.security.enabled=false
ports: - "9200:9200" - "9300:9300"
volumes: - esdata:/usr/share/elasticsearch/data
volumes:
esdata:
driver: local

# 컨테이너 시작

1. 터미널에서 docker-compose.yml 파일이 있는 디렉토리로 이동:
   cd /path/to/your/project
2. Docker Compose를 사용하여 컨테이너 시작
   docker-compose up -d

## 컨테이너 삭제 명령어

    docker-compose down

## 인덱스 삭제 명령어

curl -X DELETE "localhost:9200/recipes_elastics"
