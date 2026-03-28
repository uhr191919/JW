import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_summary(video_id):
try:
transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
text = " ".join([t['text'] for t in transcript])
prompt = f"다음 뉴스 내용을 한국어로 핵심 요약해줘: {text}"
response = model.generate_content(prompt)
print(response.text)
except Exception as e:
print(f"오류 발생: {e}")

get_summary("w3_07unTOfs")
