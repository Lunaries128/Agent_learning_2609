from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

#消息结构（System，历史，当前消息）是可以利用模板来定义

#定义提示词模板
#ChatPromptTemplate（对话提示词模板类型）创建这个ChatPromptTemplate提供了一个函数from_messages（）
#("System","content")等同于{"role":"System","content":"内容"}
#MessagesPlaceholder()
prompt=ChatPromptTemplate.from_messages([
    ("system","你是一个信息提取的AI助手，请记住用户的信息"),
    MessagesPlaceholder(variable_name="history"),
    ("human","{user_input}")
    ]
)

chat_model=init_chat_model(
    model_provider="deepseek",
    model="deepseek-v4-pro"
)

#把提示词和LLM串起来（顺序链）（1.prompt.invoke()结果交给chat_model()的invoke())
chain=prompt|chat_model

response=chain.invoke({"history":[{"role":"user","content":"我是小明"}],"user_input":"我叫什么"})

print(response.content)