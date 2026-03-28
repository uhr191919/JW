import os
from googleapiclient.discovery import build
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# 설정값 가져오기
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
YOUTUBE_KEY = os.environ["YOUTUBE_API_KEY"]
BLOOMBERG_CHANNEL_ID = "UCIALMKvObZNtJ6AmdCLP7Lg"

client = genai.Client(api_key=GEMINI_KEY)

def get_latest_video_details(channel_id):
    # 영상 제목과 상태를 알기 위해 snippet 정보를 추가로 요청합니다.
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
    items = get_latest_video_details(BLOOMBERG_CHANNEL_ID)
    print(f"총 {len(items)}개의 최신 영상을 정밀 검사합니다.")
    
    for item in items:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        live_status = item['snippet'].get('liveBroadcastContent', 'none')
        
        print(f"\n검사 중: {title} ({video_id})")
        
        if live_status == 'live':
            print("상태: 현재 생중계 중인 영상은 자막을 가져올 수 없습니다.")
            continue
            
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 수동 자막(en) 우선 검색 후 자동 자막 검색
            try:
                transcript = transcript_list.find_manual_transcript(['en'])
                print("상태: 수동 작성 자막 발견")
            except:
                transcript = transcript_list.find_generated_transcript(['en'])
                print("상태: 자동 생성 자막 발견")
                
            data = transcript.fetch()
            full_text = " ".join([t['text'] for t in data])
            
            # 제미나이 요약
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"다음 뉴스 내용을 바탕으로 경제 핵심 이슈를 한국어로 요약해줘:\n\n{full_text}"
            )
            
            print("-" * 30)
            print("요약 성공!")
            print("-" * 30)
            print(response.text)
            return
            
        except Exception as e:
            print(f"상태: 자막 추출 불가 ({str(e)})")
            continue
            
    print("\n결과: 자막이 준비된 일반 업로드 영상을 찾지 못했습니다.")

if __name__ == "__main__":
    get_summary_safe()
