import os
from googleapiclient.discovery import build
from google import genai
# 가장 표준적인 방법으로 도구를 꺼내옵니다.
from youtube_transcript_api import YouTubeTranscriptApi

# 1. API 신분증 및 채널 정보
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

client = genai.Client(api_key=GEMINI_KEY)

def get_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    # 검색 시 쇼츠(-#shorts)와 라이브 영상을 제외하여 수집 확률을 높입니다.
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        q="Bloomberg -#shorts",
        order="date",
        maxResults=15,
        type="video"
    )
    return request.execute().get('items', [])

def run():
    print("--- 시스템 진단 시작 ---")
    try:
        # 도구가 정상인지 먼저 확인합니다.
        test_attr = getattr(YouTubeTranscriptApi, 'get_transcript', None)
        print(f"도구 확인 결과: {'정상' if test_attr else '비정상(기능 없음)'}")
    except Exception as e:
        print(f"진단 중 오류: {e}")

    items = get_videos(BLOOMBERG_CHANNEL_ID)
    print(f"\n최근 블룸버그 영상 {len(items)}개를 검사합니다.")

    for item in items:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        
        # 쇼츠 필터링 (제목 검사)
        if "shorts" in title.lower():
            continue

        print(f"\n[분석 중] {title}")
        
        try:
            # 자막 데이터를 가장 직접적인 방법으로 요청합니다.
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
            full_text = " ".join([t['text'] for t in transcript])
            
            print(f"-> 자막 성공! (텍스트 길이: {len(full_text)}자)")

            # 제미나이 2.0 모델에게 경제 브리핑 요청
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 자막을 경제 전문가의 시각으로 한국어 요약해줘:\n\n{full_text}"
            )
            
            print("\n" + "★" * 30)
            print("블룸버그 투데이 뉴스 리포트")
            print(f"영상: {title}")
            print("★" * 30)
            print(response.text)
            return # 하나라도 성공하면 종료

        except Exception as e:
            # 에러 내용을 더 구체적으로 출력하여 지웅님께 알려드립니다.
            print(f"-> 건너뜀 사유: {str(e).split('.')[0]}")
            continue

    print("\n최종 결과: 요약 가능한 유효 자막이 있는 영상을 찾지 못했습니다.")

if __name__ == "__main__":
    run()
