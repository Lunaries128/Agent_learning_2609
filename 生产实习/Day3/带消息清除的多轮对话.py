from dashscope.acli.compression import compress_messages
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import  dotenv

from 生产实习.Day2.chatbox import ai_message

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.7-max",
    streaming=True,
)

messages=[]

while True:
    user_input=input("你(quit退出 clear清除记忆):").strip()

    if user_input=="quit":
        break

    if user_input=="clear":
        messages=[]
        print("记忆已完全清除！！！")
        continue
    if user_input=="history":
        for m in messages:
            print(m)
        continue

    if user_input=="compress":
        if len(messages)>7:
            history_messages=messages[0:-6]
            old_messages=""
            for mess in history_messages:
                role = "user" if mess.type=="human" else "assistant"
                old_messages += f"{role}:"+mess["content"]+"\n"

            compress_messages=[
                SystemMessage(
                    content="你是一个文本摘要助手，请把下面对话的历史消息压缩成一段简短的前情提要（不超过50个字），保留关键的信息，去掉废话。只输出摘要的内容，不要加任何的前缀。"
                ),
                HumanMessage(content=old_messages)
            ]

            llm=ChatOpenAI(
                model="qwen3.7-max",
                temperature=0.3,
                max_tokens=200
            )

            compress_response=llm.invoke(compress_messages)
            messages=messages[-6:]
            message.insert(0,compress_response)


    #一个HumanMessage=={"role":"user","content":""}
    messages.append(chat_model.chat(user_input))

    response=chat_model.stream(user_input)

    ai_message=""
    for message in response:
        if message.content=="":
            continue
        ai_message+=message.content
        print(message.content,end="",flush=True)

    messages.append(AIMessage(content=ai_message))

    print()