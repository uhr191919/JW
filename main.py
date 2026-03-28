import os
from googleapiclient.discovery import build
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# 1. 설정값
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

client = genai.Client(api_key=GEMINI_KEY)

def get_latest_videos(channel_id):
    """검색 범위를 15개로 늘립니다."""
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        order="date",
        maxResults=15, # 5개에서 15개로 확장
        type="video"
    )
    response = request.execute()
    return [item['id']['videoId'] for item in response['items']]

def get_summary_safe():
    video_ids = get_latest_videos(BLOOMBERG_CHANNEL_ID)
    print(f"총 {len(video_ids)}개의 영상을 검사합니다...")
    
    for video_id in video_ids:
        try:
            # 수동 자막뿐만 아니라 자동 생성된 자막까지 모두 검색합니다.
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 영어 자막(en)을 먼저 찾고, 없으면 영어 계열 자막을 아무거나 가져옵니다.
            try:
                transcript = transcript_list.find_manual_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['en'])
                
            data = transcript.fetch()
            full_text = " ".join([t['text'] for t in data])
            
            # 요약 실행
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 블룸버그 뉴스 내용을 바탕으로 주요 경제 지표와 이슈를 한국어로 요약해줘:\n\n{full_text}"
            )
            
            print("=" * 30)
            print(f"브리핑 성공! 영상 ID: {video_id}")
            print(f"영상 주소: https://youtu.be/{video_id}")
            print("=" * 30)
            print(response.text)
            return
            
        except Exception:
            # 로그를 간결하게 하기 위해 조용히 다음 영상으로 넘어갑니다.
            continue
            
    print("현재 자막이 준비된 최신 영상이 없습니다. 잠시 후 다시 시도해 주세요.")

if __name__ == "__main__":
    get_summary_safe()
