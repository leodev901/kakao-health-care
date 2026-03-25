import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field 
from google import genai

load_dotenv(".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# 잘못된 입력 → 400 Bad Request
# 4xx → 권한
# LLM upstream 이상한 응답을 줌 → 502 
# LLM upstream 일시 사용 불가 → 503
# 서버 내부 오류  → 500 Internal Server Error

app = FastAPI()

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="사용자 질의")

class ChatResponse(BaseModel):
    answer: str 

def call_llm(query:str)->str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=query
    )
    return response.text.strip()


def handle_request(query: str) -> ChatResponse:
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=400, detail="입력 값이 올바르지 않습니다.")

    try:
        response = call_llm(clean_query)
    
        if not response:
            raise HTTPException(status_code=502, detail="LLM 결과가 없습니다.")
        
        return ChatResponse(answer=response)
    
    except HTTPException as e :
        print(f"Exception: {e}")
        raise e
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail="LLM 호출 과정에서 오류가 발생 했습니다.")

    


@app.post("/chat", response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest) -> ChatResponse:

    result = handle_request(payload.query)
    return result
