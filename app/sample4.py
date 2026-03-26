import os
from dotenv import load_dotenv
from openai import OpenAI
from google import genai

load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")


documents = [
    "내과 예약은 평일 09시부터 17시까지 가능합니다.",
    "실손보험 청구는 진료비 결제 후 진행할 수 있습니다.",
    "건강검진 결과는 마이데이터 화면에서 확인할 수 있습니다."
]


def retrieve_documents(query:str, documents:list[str], top_k:int =2)->list[str]:
    keywords = query.split()
    scored = []

    for doc in documents:
        sum = 0
        for keyword in keywords:
            if keyword in doc:
                sum+=1
        scored.append((sum,doc))
    
    
    ranked_doc = sorted(scored, key=lambda scored:scored[0], reverse=True)
    # for d in ranked_doc:
    #     print(d)   
    return ranked_doc[:top_k]
    

def build_context(contexts) -> str:
    build = ""
    for context in contexts:
        build += context[1] + "\n"
    return build
    

def generate_answer(query: str, contexts: list[str]) -> str:

    
    prompt = f"""다음 주어진 문맥을 활용하여 사용자 질문에 답변하세요 
문맥: {build_context(contexts)}
질문: {query}
"""
    print(prompt)

    # client = OpenAI(api_key=OPENAI_API_KEY)
    # response = client.responses.create(
    #     model=OPENAI_MODEL,
    #     input=prompt,
    # )
    # answer = response.output_text.strip()
    

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    answer = response.text.strip()

    return answer

def answer_question(query:str, documents:list[str]):
    contexts = retrieve_documents(query,documents)
    return generate_answer(query,contexts)

if __name__ == "__main__":
    query = input("질문: ").strip()
    answer = answer_question(query, documents)
    print(answer)

    # 예약 보험 청구 결제 결과는?
