import os
import dotenv
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI()

while True:
    user_input = input("你(quit 退出):").strip()
    if user_input == "quit":
        print("再见!!!")
        break

    completion = client.chat.completions.create(
        model="qwen3.7-max",
        messages=[{"role":"user","content":user_input}],
        stream=True
    )

    is_reason=True

    print("="*50+"推理过程"+"="*50)

    for chunk in completion:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.reasoning_content:
            print(delta.reasoning_content,end="",flush=True)
        if delta.content:
            if is_reason:
                print()
                is_reason=False
                print("="*50+"结果"+"="*50)
            print(delta.content,end="",flush=True)

    print()

"""
直接输出推理过程和结果
print("="*50+"推理过程"+"="*50)
print(completion.choices[0].message.reasoning_content)
print("="*50+"结果"+"="*50)
print(completion.choices[0].message.content)
"""




