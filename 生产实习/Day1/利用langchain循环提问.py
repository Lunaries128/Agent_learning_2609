import os
import dotenv
from langchain.chat_models import init_chat_model

dotenv.load_dotenv()

client = init_chat_model(
    model_provider="openai",
    model="qwen3.8-max"
)

while True:
    user_input=input("你(quit 退出):").strip()
    if user_input=="quit":
        break

    is_reason=True


    for chunk in client.stream(user_input):
        if not chunk.content:
            continue

        """
        langchain的框架默认只保留最终回答内容，主动丢弃了模型返回的推理字段
        if 'reasoning_content' in chunk.additional_kwargs and chunk.additional_kwargs['reasoning_content']:
            print(chunk.additional_kwargs['reasoning_content'], end="", flush=True)
        """

        if chunk.content:
            if is_reason:
                is_reason = False
                print("="*50+"结果"+"="*50)
            print(chunk.content, end="", flush=True)

    print()







