from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.7-max",
    streaming=True,
)

#就是以后存储每次对话的历史消息的列表
messages=[]

while True:
    user_input=input("你（quit 退出）:").strip()

    if user_input == "quit":
        print(f"历史消息:{len(messages)}")
        break

    messages.append({"role":"user","content":user_input})

    response=chat_model.stream(messages)

    ai_message=""

    for message in response:
        if message.content == "":
            continue
        ai_message += message.content
        print(message.content,end="",flush=True)

    message.append({"role":"message","content":ai_message})

    print()

"""
目前版本实现了短期记忆功能
bug：
  短期记忆是利用一个消息列表，把每次对话的用户消息以及AI的回复消息（一次对话产生两个消息）随着对话的次数增加，消息列表会不断增长
  1.token问题：token的消耗（提示词、推理和结果都是计算token的），比如第n轮对话（提示词包含前面n-1*2条消息的）
  2.上下文问题：提示词、推理和结果都是上下文的内容，上下文是有限制的
  3.噪声问题：数据越大，噪声就会越大，结果一定不精确的
  4.性能问题
  
解决方案：
  1.清除（算法）10论对话，把之前的全部清除
  2.压缩摘要：只保留最近的3轮对话消息，超过3轮之前的对话消息，让模型给我生成消息摘要（把多条消息压缩成一条消息）既有记忆又兼容了上述的bug
"""