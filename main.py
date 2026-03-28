import os
from googleapiclient.discovery import build
from google import genai
import youtube_transcript_api as yta # 이름을 바꿔서 충돌을 방지합니다.

# 1. 환경 설정
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

client = genai.Client(api_key=GEMINI_KEY)

def get_latest_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    # 생중계 중인 영상은 자막 수집이 불가능하므로 일반 영상만 검색합니다.
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        order="date",
        maxResults=15,
        type="video",
        safeSearch="none"
    )
    response = request.execute()
    return response['items']

def get_summary_safe():
    items = get_latest_videos(BLOOMBERG_CHANNEL_ID)
    print(f"총 {len(items)}개의 후보 영상을 정밀 분석합니다...")
    
    for item in items:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        # 현재 생중계 여부를 다시 한번 체크합니다.
        live_status = item['snippet'].get('liveBroadcastContent', 'none')
        
        if live_status == 'live':
            print(f"-> [건너뜀] 생중계 중인 영상: {title}")
            continue
            
        print(f"-> [시도 중] {title} ({video_id})")
        
        try:
            # yta 모듈의 YouTubeTranscriptApi 클래스를 직접 참조합니다.
            transcript_list = yta.YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
            full_text = " ".join([t['text'] for t in transcript_list])
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 내용을 경제 전문가 관점에서 한국어로 핵심 요약해줘:\n\n{full_text}"
            )
            
            print("=" * 40)
            print(f"성공! 요약 영상: {title}")
            print(f"URL: https://youtu.be/{video_id}")
            print("=" * 40)
            print(response.text)
            return
            
        except Exception as e:
            # 구체적인 에러 내용을 파악하기 위해 메시지를 출력합니다.
            print(f"   ㄴ 자막 로드 실패: {str(e).split('.')[0]}")
            continue
            
    print("\n최종 결과: 요약 가능한 자막이 있는 영상을 찾지 못했습니다.")

if __name__ == "__main__":
    get_summary_safe()
