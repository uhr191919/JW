import os
from googleapiclient.discovery import build
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# 1. 설정값 가져오기
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

# 2. 제미나이 최신 클라이언트 설정 (2026년 표준)
client = genai.Client(api_key=GEMINI_KEY)

def get_latest_videos(channel_id):
    """최신 영상 5개를 가져옵니다."""
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        order="date",
        maxResults=5,
        type="video"
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response['items']]

def get_summary_safe():
    """자막이 있는 최신 영상을 찾아 요약합니다."""
    video_ids = get_latest_videos(BLOOMBERG_CHANNEL_ID)
    
    for video_id in video_ids:
        try:
            # 자막 목록을 먼저 확인하여 영어 자막(자동 생성 포함)을 가져옵니다.
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en'])
            data = transcript.fetch()
            
            full_text = " ".join([t['text'] for t in data])
            
            # 제미나이 2.0 모델을 사용한 최신 요약 방식
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 자막을 경제 전문가의 시선으로 핵심 요약해줘:\n\n{full_text}"
            )
            
            print("=" * 30)
            print(f"성공! 요약 영상 ID: {video_id}")
            print("오늘의 블룸버그 뉴스 브리핑")
            print("=" * 30)
            print(response.text)
            return # 성공하면 종료
            
        except Exception as e:
            print(f"영상({video_id}) 자막을 가져올 수 없어 다음 영상을 시도합니다.")
            continue
            
    print("최근 5개 영상 중 요약 가능한 자막이 있는 영상이 없습니다.")

if __name__ == "__main__":
    get_summary_safe()
