MongoDB 초기 웹사이트 설정할 때 'Driver' connect.

conda create -n ace_final_test python=3.12
conda activate ace_final_test
pip install fastapi uvicorn beautifulsoup4 requests lxml fake_useragent python-dotenv "pymongo[srv]"
cd [해당폴더]
uvicorn main:app --reload --port=[포트번호]

# 엘라스틱서치 구현

pip install elasticsearch

# 엘라스틱서치 Docker 이미지 설치

docker pull docker.elastic.co/elasticsearch/elasticsearch:7.15.2

# 엘라스틱서치 컨테이너 실행

docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.15.2
