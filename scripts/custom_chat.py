from mlx_lm import load, stream_generate

print("🧠 완성된 뇌세포를 탑재한 단일 모델을 불러오는 중입니다...")
model, tokenizer = load("./my-custom-bllossom")

# AI가 대화의 맥락을 기억할 수 있도록 '기억(History)' 변수 세팅
history = [
    {"role": "system", "content": "당신은 친절하고 똑똑한 사내 챗봇입니다. 질문에 문맥을 파악하여 자연스럽게 대답하세요."}
]

print("\n=======================================")
print("🤖 AI 대화방이 열렸습니다! (종료하려면 'quit' 입력)")
print("=======================================\n")

while True:
    user_input = input("😎 사용자: ")

    if user_input.lower() == 'quit':
        print("대화를 종료합니다.")
        break

    # 1. 사용자의 말을 기억에 저장
    history.append({"role": "user", "content": user_input})

    # 2. Llama-3 대화형 규격으로 포장
    prompt = tokenizer.apply_chat_template(
        history,
        tokenize=False,
        add_generation_prompt=True
    )

    # 🚨 핵심 안전장치 1: 만약 토크나이저가 숫자 리스트(list)를 뱉었다면 강제로 문자로 해독(decode)
    if isinstance(prompt, list):
        prompt = tokenizer.decode(prompt)

    # 🚨 핵심 안전장치 2: 무슨 일이 있어도 무조건 문자열(str)로 고정
    prompt = str(prompt)

   # 3. 답변 생성 (답변을 덩어리째 받지 않고, 한 글자씩 실시간으로 받습니다!)
    print("🤖 AI 답변: ", end="", flush=True)
    clean_response = ""

    # generate 대신 stream_generate를 사용하여 글자가 생성될 때마다 바로바로 화면에 출력합니다.
    for chunk in stream_generate(model, tokenizer, prompt, max_tokens=150):
        # 최신 MLX 버전에 맞춘 안전장치
        text = chunk.text if hasattr(chunk, 'text') else str(chunk)
        
        # 특수 마침표가 나오면 즉시 출력 중단
        if "<|eot_id|>" in text:
            break
            
        print(text, end="", flush=True)
        clean_response += text
        
    print("\n")

    # 4. AI의 대답도 기억에 저장
    history.append({"role": "assistant", "content": clean_response})