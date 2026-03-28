import os
from googleapiclient.discovery import build
from google import genai
import youtube_transcript_api # 클래스를 직접 import하지 않고 모듈로 가져옵니다.

# 1. API 신분증 설정
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

client = genai.Client(api_key=GEMINI_KEY)

def get_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        order="date",
        maxResults=10, # 최근 영상 10개를 훑습니다.
        type="video"
    )
    return request.execute().get('items', [])

def run():
    videos = get_videos(BLOOMBERG_CHANNEL_ID)
    print(f"분석 시작: {len(videos)}개의 영상을 스캔합니다.")

    for v in videos:
        video_id = v['id']['videoId']
        title = v['snippet']['title']
        print(f"\n[검사 중] {title} ({video_id})")

        try:
            # 모듈 내의 클래스를 직접 참조하여 AttributeError를 원천 차단합니다.
            api = youtube_transcript_api.YouTubeTranscriptApi
            transcript = api.get_transcript(video_id, languages=['en'])
            
            full_text = " ".join([t['text'] for t in transcript])
            print(f"-> 자막 추출 성공! ({len(full_text)}자)")

            # 제미나이 2.0 플래시로 요약 요청
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 내용을 경제 전문가 관점에서 한국어로 핵심 요약해줘:\n\n{full_text}"
            )
            
            print("\n" + "="*40)
            print(f"★ 오늘의 뉴스 브리핑 ★")
            print(f"영상: {title}")
            print("="*40)
            print(response.text)
            return # 요약 성공 시 즉시 종료

        except Exception as e:
            # 자막이 아직 처리 중이거나 없는 경우 다음 영상으로 넘어갑니다.
            print(f"-> 건너뜀: {str(e)[:50]}...")
            continue

    print("\n최종 결과: 현재 자막 데이터가 준비된 영상을 찾지 못했습니다.")

if __name__ == "__main__":
    run()
