import os
from googleapiclient.discovery import build
from google import genai
import youtube_transcript_api

# 1. 환경 변수 및 채널 설정
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

# 2. 제미나이 AI 클라이언트 설정
client = genai.Client(api_key=GEMINI_KEY)

def get_latest_news_videos(channel_id):
    # 검색어에 -#shorts를 추가하여 쇼츠 영상을 1차 필터링합니다.
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        q="Bloomberg -#shorts",
        order="date",
        maxResults=15,
        type="video"
    )
    response = request.execute()
    return response.get('items', [])

def process_summary():
    video_items = get_latest_news_videos(BLOOMBERG_CHANNEL_ID)
    print(f"분석 시작: {len(video_items)}개의 후보 영상을 정밀 검사합니다.")

    for item in video_items:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        
        # 제목에 shorts 키워드가 포함된 경우 2차로 제외합니다.
        if "shorts" in title.lower():
            continue

        print(f"검사 대상 발견: {title} ({video_id})")

        try:
            # 모듈 전체를 통해 클래스에 접근하여 AttributeError를 방지합니다.
            api_class = youtube_transcript_api.YouTubeTranscriptApi
            transcript = api_class.get_transcript(video_id, languages=['en', 'en-US'])
            
            full_text = " ".join([t['text'] for t in transcript])
            
            # 텍스트가 너무 짧은 영상은 정보량이 부족하므로 건너뜁니다.
            if len(full_text) < 300:
                print("-> 정보량이 부족한 영상입니다. 다음 영상으로 넘어갑니다.")
                continue

            # 제미나이 2.0 모델을 사용한 핵심 요약 요청
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 자막을 경제 전문가의 시각으로 한국어 요약해줘:\n\n{full_text}"
            )
            
            print("\n" + "="*40)
            print("블룸버그 뉴스 데일리 브리핑")
            print(f"영상 제목: {title}")
            print("="*40)
            print(response.text)
            return

        except Exception as e:
            # 자막 데이터가 아직 생성되지 않은 경우 조용히 다음 영상을 시도합니다.
            print(f"-> 자막 데이터를 가져올 수 없습니다. (사유: {str(e)[:50]}...)")
            continue

    print("\n최종 결과: 요약 가능한 충분한 텍스트 정보가 있는 영상을 찾지 못했습니다.")

if __name__ == "__main__":
    process_summary()
