import os
import sys
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

HISTORY_SIZE = 6




# [ {"role":"user", "content":"..."}, {"role":"assistant", "content":"..."} ... ] 

def build_prompt(query:str,memory:list[dict])->list[dict]:
    prompt = [
        {"role":"system", "content":"You are a helpful assistant."}
    ]
    prompt.extend(memory[:])
    prompt.append({"role":"user", "content":query})

    return prompt



def call_llm(query: str,memory:list[dict]) -> str:
    
    prompt = build_prompt(query,memory)

    print("="*50)
    for message in prompt:
        print(message)

    try:
        # ======== OEPNAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )
        answer = response.output_text
        return answer
    
    except Exception :
        # return "LLM 호출 오류 발생"
        raise
    

    


def chat() -> None:

    # initial
    chat_memory:list[dict] = []
    
    while True:

        user_input = sys.stdin.readline().strip()

        if not user_input:
            continue
    
        if user_input.lower()=="exit":
            break

        memory=chat_memory[:]    
        answer = call_llm(user_input,memory).strip()

        print(answer)


        chat_memory.append({"role":"user", "content":user_input})
        chat_memory.append({"role":"assistant", "content":answer})
        chat_memory = chat_memory[-HISTORY_SIZE:]






if __name__ == "__main__":
    chat()