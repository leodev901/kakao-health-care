DEFAULT_CITY = "서울"

def classify_intent(user_input: str) -> str:
    intent_keywords = [
        ("날씨",["날씨","날씨는","기상"]),
        ("예약",["예약","예약가능"]),
    ]
    for intent, keywords in intent_keywords:
        if any(word in user_input for word in keywords):
            return intent
    return "기타"

def dispatch_func(intent: str, user_input: str) -> str:
    TOOL_CALL = {
        "날씨": handle_weather,
        "기타": handle_general,
    }
    if intent == "날씨":
        return TOOL_CALL[intent]()
    else:
        return TOOL_CALL[intent](user_input)
    


def handle_weather(city: str = DEFAULT_CITY) -> str:
    return f"{city} 날씨는 맑음입니다."

def handle_general(user_input: str) -> str:
    return f"일반 답변: {user_input}"

def main() -> None:
    user_input = input("질문: ").strip()
    if not user_input:
        print("질문을 입력해주세요")
        return
    
    intent = classify_intent(user_input)

    try:
        answer = dispatch_func(intent, user_input)
    except Exception as e:
        print(e)
        raise ValueError("Tool 호출 실패")

    print(answer)
    
if __name__ == "__main__":
    main()