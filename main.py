import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# 1. 제미나이 API 설정
# 깃허브 설정에 등록한 GEMINI_API_KEY를 자동으로 가져옵니다.
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_summary(video_id):
    # 2. 뉴스 요약 함수 정의
    # def 다음 줄부터는 반드시 4칸의 빈칸이 있어야 합니다.
    try:
        # 유튜브 자막을 영어로 가져옵니다.
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        text = " ".join([t['text'] for t in transcript])
        
        # 제미나이에게 한글 요약을 요청하는 명령문입니다.
        prompt = f"다음 뉴스 자막 내용을 바탕으로 핵심 이슈를 한국어로 요약해줘:\n\n{text}"
        response = model.generate_content(prompt)
        
        # 결과를 화면에 출력합니다.
        print("=" * 30)
        print("뉴스 브리핑 결과")
        print("=" * 30)
        print(response.text)
        
    except Exception as e:
        # 오류가 발생할 경우 내용을 출력합니다.
        print(f"작업 중 오류가 발생했습니다: {e}")

# 3. 프로그램 실제 실행 부분
if __name__ == "__main__":
    # 테스트를 위한 뉴스 영상 ID입니다.
    # 나중에 다른 뉴스를 보고 싶다면 이 ID 값만 바꾸면 됩니다.
    get_summary("w3_07unTOfs")
