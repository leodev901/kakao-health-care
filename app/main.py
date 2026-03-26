import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from google import genai
from loguru import logger


load_dotenv(".env")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
OPENAI_MODEL=os.getenv("OPENAI_MODEL")

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GEMINI_MODEL=os.getenv("GEMINI_MODEL")


DOCUMENTS = [
    "내과 예약은 평일 09시부터 17시까지 가능합니다.",
    "실손보험 청구는 진료비 결제 후 진행할 수 있습니다.",
    "건강검진 결과는 마이데이터 화면에서 확인할 수 있습니다.",
    "예약 변경은 진료 예약 메뉴에서 가능합니다."
]

SESSION_HISTORY: dict[list] = {}
MAX_HISTORY_SIZE = 6

DEFAULT_DEPARTMENT = "내과"
DEFAULT_CITY = "서울"



app = FastAPI(
    title="카카오 헬스케어 실습"
)

class ChatRequest(BaseModel):
    session_id:str
    message:str 

class ChatResponse(BaseModel):
    answer:str
    source:str


def classify_intent(message:str) -> str:
    intent_keywords = [
        ("tool",["예약", "시간"]),
        ("rag",["실손보험", "건강검진", "마이데이터" ])
        # "chat"
    ]

    for intent, keywords in intent_keywords:
        if any(word in message for word in keywords):
            return intent
    return "기타"


def get_available_slots(department: str = DEFAULT_DEPARTMENT) -> str:
    return f"{department} 예약 가능한 시간은 15:00~18:00 입니다."

def get_weather(city: str = DEFAULT_CITY) -> str:
    return f"{city} 날씨는 맑음입니다."



def handle_tool(message:str) -> str:
    if "예약" in message:
        try:
            return get_available_slots("내과")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code="502",detail="예약 도구 사용중 오류가 발생하였습니다.")
    elif "날씨" in message:
        try:
            return get_weather("서울")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code="502",detail="날씨 도구 사용중 오류가 발생하였습니다.")
    else:
        return "적절한 도구가 없습니다."

def build_history(history:dict)->list:
    return [ f" 'role':{h['role']}, 'content':{h['content']}" for h in history ]


def call_llm(session_id:str,message:str,client:genai.Client,contenxt:list[str]=None)->str:
    context_str = "\n".join(contenxt) if contenxt else "(없음)" 
    history_str = "\n".join(build_history(SESSION_HISTORY[session_id])) if SESSION_HISTORY[session_id] else "(없음)"

    prompt = f"""
다음 문맥과 히스토리를 참고하여 현재 질문에 답하라.
문맥:{context_str}
히스토리:{history_str}
현재질문:{message}
""" 
    print(prompt)
    try:
        response=client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        logger.error(e)
        # raise HTTPException(status_code=500,detail="LLM 호출에 오류가 발생하였습니다.")


def handle_rag(session_id:str,message:str, client: genai.Client, top_k:int=2)->str:
    keywords = message.split()
    scored_doc = [] # [ (socre,doc),  ]

    for doc in DOCUMENTS:
        score = sum( 1 for word in keywords if word in doc )
        if score > 0:
            scored_doc.append( (score, doc) )
    
    if len(scored_doc) == 0:
        return "일치하는 문맥이 없습니다."
    
    scored_doc.sort( key=lambda x:x[0], reverse=True)
    
    context = [ doc for socre, doc in scored_doc[:top_k]  ]

    # print(context)
    # return ""
    return call_llm(session_id,message,client,context)



def handle_request(session_id:str, message:str) -> ChatResponse:
    clean_message = message.strip()

    client = genai.Client(api_key=GEMINI_API_KEY)
    if session_id not in SESSION_HISTORY:
        SESSION_HISTORY[session_id] = []


    if not clean_message:
        raise HTTPException(status_code=400, detail="입력값이 없습니다.")
    
    intent = classify_intent(clean_message)

    if intent=="tool":
        answer = handle_tool(clean_message)
    elif intent=="rag":
        answer = handle_rag(session_id,clean_message,client)
    else:
        answer = call_llm(session_id, clean_message,client)
    
    if not answer.strip():
        answer="생성된 답변이 없습니다."
    
    

    SESSION_HISTORY[session_id].append({"role":"user","content":clean_message})
    SESSION_HISTORY[session_id].append({"role":"assistant","content":answer})

    SESSION_HISTORY[session_id] = SESSION_HISTORY[session_id][-6:]


    return ChatResponse(
        answer=answer,
        source=intent,
    )

    




@app.post("/agent/chat", response_model=ChatResponse)
def agent_chat(reuqest:Request, payload:ChatRequest) -> ChatResponse:
    return handle_request(payload.session_id, payload.message)


# if __name__ == "__main__":
#     # print(handle_tool("날씨"))
#     # print(handle_tool("예약"))
#     # print(handle_tool("기타"))
#     session_id="user001"
#     client = genai.Client(api_key=GEMINI_API_KEY)
#     if session_id not in SESSION_HISTORY:
#         SESSION_HISTORY[session_id] = []
#     call_llm(session_id,"call",client,["안녕하세요 문맥입니다.","this is context for query"])

#     print(call_llm(session_id,"질문입니다.",client,["안녕하세요 문맥입니다.","this is context for query"]))