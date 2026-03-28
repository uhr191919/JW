import os
from googleapiclient.discovery import build
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

client = genai.Client(api_key=GEMINI_KEY)

def get_latest_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        order="date",
        maxResults=20,
        type="video"
    )
    response = request.execute()
    return response['items']

def get_summary_safe():
    items = get_latest_videos(BLOOMBERG_CHANNEL_ID)
    print(f"총 {len(items)}개의 블룸버그 영상을 정밀 스캔합니다.")
    
    for item in items:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        print(f"\n검사 중: {title} ({video_id})")
        
        try:
            # 다양한 영어 자막 형식을 시도합니다.
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])
            full_text = " ".join([t['text'] for t in data])
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 뉴스 내용을 바탕으로 주요 경제 지표와 이슈를 한국어로 요약해줘:\n\n{full_text}"
            )
            
            print("=" * 35)
            print(f"성공! 요약 영상: {title}")
            print("=" * 35)
            print(response.text)
            return
            
        except Exception as e:
            # 에러 메시지의 앞부분을 출력하여 원인을 파악합니다.
            error_msg = str(e).split('\n')[0]
            print(f"-> 건너뜀 사유: {error_msg}")
            continue
            
    print("\n최종 결과: 현재 자막이 준비된 영상을 찾지 못했습니다.")

if __name__ == "__main__":
    get_summary_safe()
