conda create -n ace_final_test python=3.12
conda activate ace_final_test
pip install fastapi uvicorn beautifulsoup4 requests lxml fake_useragent python-dotenv "pymongo[srv]"
cd [해당폴더]
uvicorn main:app --reload --port=[포트번호]
