from langchain_openai import ChatOpenAI
import  dotenv

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.7-max",
    streaming=True,
)

while True:
    user_input=input("你（quit 退出:").strip()

    if user_input=="quit":
        break
    response=chat_model.stream(user_input)

    for message in response:
        if message.content=="":
            continue
        print(message.content,end="",flush=True)
    print()