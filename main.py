import os
from googleapiclient.discovery import build
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# 1. 신분증 확인
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

# 2. 제미나이 2026 표준 클라이언트
client = genai.Client(api_key=GEMINI_KEY)

def get_latest_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        order="date",
        maxResults=15,
        type="video"
    )
    response = request.execute()
    return response['items']

def get_summary_safe():
    items = get_latest_videos(BLOOMBERG_CHANNEL_ID)
    print(f"총 {len(items)}개의 블룸버그 뉴스를 스캔합니다...")
    
    for item in items:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        
        try:
            # 영어 자막(자동 생성 포함)을 가져오는 가장 안정적인 명령어입니다.
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
            full_text = " ".join([t['text'] for t in data])
            
            # 제미나이에게 요약 요청
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 내용을 바탕으로 경제 핵심 이슈를 한국어로 요약해줘:\n\n{full_text}"
            )
            
            print("=" * 35)
            print(f"성공! 요약 영상: {title}")
            print(f"주소: https://youtu.be/{video_id}")
            print("=" * 35)
            print(response.text)
            return # 성공 시 종료
            
        except Exception:
            # 자막이 없는 영상(Shorts 등)은 조용히 건너뜁니다.
            continue
            
    print("현재 요약 가능한 자막이 있는 영상이 없습니다. 잠시 후 시도해 주세요.")

if __name__ == "__main__":
    get_summary_safe()
