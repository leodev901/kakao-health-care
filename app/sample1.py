import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai

load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")



def get_weather(city: str) -> str:
    return f"오늘 {city} 날씨는 맑음 입니다."    

def get_available_slots(department: str) -> str:
    return f"{department} 예약 가능한 시간은 15:00~18:00 입니다."

def call_llm(query: str) -> str:
    try:
        # ======== OEPNAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=query
        )
        answer = response.output_text
        return answer

        # ======== GEMINI
        # client = genai.Client(api_key=GEMINI_API_KEY)
        # response = client.models.generate_content(
        #     model=GEMINI_MODEL,
        #     contents=query,
        # )
        # answer = response.text.strip()
        return answer
    except Exception as e:
        return(f"LLM 호출 오류 발생 {e}")




def classify_intent(query:str)->str:
    intent_keywords={
        "날씨":["날씨"],
        "예약":["예약","가능","시간","취소"]
    }

    for intent in intent_keywords:
        if any(keyword in query for keyword in intent_keywords[intent]):
            return intent
    
    return "기타"

def handel_request(user_input) -> str:
    intent = classify_intent(user_input)

    if intent == "날씨":
        return get_weather("서울")
    elif intent == "예약":
        return get_available_slots("내과")
    else: 
        return call_llm(user_input)

if __name__ == "__main__":

    query_list = [
        "오늘 날씨는 어때?",
        "예악 가능한 시간은 언제야?",
        "대한민국의 수도는?",
    ]

    for i, query in enumerate(query_list,1):
        print(f"{i}. {handel_request(query)}")