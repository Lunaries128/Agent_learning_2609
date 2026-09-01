import os
import dotenv
from langchain.chat_models import init_chat_model

dotenv.load_dotenv()

client = init_chat_model(
    model_provider="openai",
    model="qwen3.7-max",
        # 因为openai和langchain底层设计差异，需要增加开启推理开关
    extra_body={
        "enable_thinking": True
        }
)

while True:
    user_input=input("你(quit 退出):").strip()
    if user_input=="quit":
        break

    is_reason=True

    print("="*50+"推理过程"+"="*50)
    for chunk in client.stream(user_input):
        if not chunk.content:
            continue

        if 'reasoning_content' in chunk.additional_kwargs and chunk.additional_kwargs['reasoning_content']:
            print(chunk.additional_kwargs['reasoning_content'], end="", flush=True)

        if chunk.content:
            if is_reason:
                is_reason = False
                print("="*50+"结果"+"="*50)
            print(chunk.content, end="", flush=True)

    print()







