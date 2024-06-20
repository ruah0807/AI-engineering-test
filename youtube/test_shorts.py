###유튜브 숏츠 자막 빼오기 ###

# youtube-transcript-api 라이브러리 설치
# !pip install youtube-transcript-api

from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# URL에서 비디오 ID 추출
def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/shorts/'):
            return parsed_url.path.split('/')[2]
    return None

# 자막 가져오기
def get_subtitles(url, language='ko'):
    # video_id 추출 부분 수정 없음
    video_id = extract_video_id(url)
    if not video_id:
        return "Invalid YouTube URL"
    
    try:
        # 언어 매개변수를 전달하도록 수정
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        subtitles = ' '.join([entry['text'] for entry in transcript])
        return subtitles
    except Exception as e:
        return str(e)
    
    
    
#테스트용 유튜브 url
video_url = 'https://youtube.com/shorts/1eh4JKEgIio?si=IC-TmM_U0dNlds8E'
subtitles = get_subtitles(video_url)
print(subtitles)



#api_key='db31f186-85fc-4d80-a8f7-45b3c4488b1b'

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

#Pinecone 초기화
pc = Pinecone(api_key='api-key-넣어야함')

index_name = 'youtube-subtitles'

# 기존 인덱스 삭제 (예외 처리 추가)
try:
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
except Exception as e:
    print(f"Error deleting index: {str(e)}")


#인덱스 생성

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

index = pc.Index(index_name)

#임베딩 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 자막을 백터로 변환
embeddings = model.encode(subtitles).tolist()
# print(embeddings)

# 데이터 삽입
index.upsert(vectors=[('video1', embeddings)])


# 저장된 벡터 조회
# fetched_vector = index.fetch(ids=['video1'])
# print(fetched_vector)


# 유사도 검색 함수
def find_similar_videos(query_text):
    query_embedding = model.encode(query_text).tolist()
    results = index.query(vector=query_embedding, top_k=5)
    # print(results)
    return results['matches']

# 예제 사용
query_text = '냉동 만두 열 개, 숙주 한 줌, 청양고추 두 개, 대파 1/4 쪽, 고춧가루 한 스푼, 물 600ml, 국간장 반 스푼, 멸치액젓 한 스푼, 코인 육수 두 알, 냉동만두 일곱 개, 계란 하나, 후추.'
similar_videos = find_similar_videos(query_text)
print(similar_videos)