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

# 테스트용 유튜브 URL
video_url = 'https://youtube.com/shorts/1eh4JKEgIio?si=IC-TmM_U0dNlds8E'
# get_subtitles 함수에 language 매개변수 추가
subtitles = get_subtitles(video_url)
print(subtitles)