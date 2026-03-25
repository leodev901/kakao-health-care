import re

documents = [
    "내과 예약은 평일 09시부터 17시까지 가능합니다.",
    "실손보험 청구는 진료비 결제 후 진행할 수 있습니다.",
    "건강검진 결과는 마이데이터 화면에서 확인할 수 있습니다."
]

STOPWORDS = {
    "은", "는", "이", "가", "을", "를", "에", "의", "와", "과",
    "좀", "문의", "알려줘", "알려주세요", "가능", "가능한가요",
    "어디", "어디서", "언제", "무엇", "뭐", "인가요", "있나요"
}


def retrieve_documents(query:str, documents:list[str], top_k:int =2)->list[str]:
    contexts = []
    return contexts

def answer_question(query:str, documents:list[str]):
    contexts = retrieve_documents(query,documents)
    return generate_answer(query,contexts)

if __name__ == "__main__":
    query = input("질문: ").strip()
    answer = answer_question(query,documents)
    print(answer)
