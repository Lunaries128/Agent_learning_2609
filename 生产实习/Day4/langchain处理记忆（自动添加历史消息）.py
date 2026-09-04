from langchain.chat_models import init_chat_model
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import dotenv
from langchain_core.runnables import RunnableWithMessageHistory

dotenv.load_dotenv()

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

chain=prompt|chat_model

#定义sessions变量（Dict字典类型）
sessions={}

def get_session_history(session_id:str)->InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id]=InMemoryChatMessageHistory()
    return sessions[session_id]

chat_with_history=RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="user_input",
    history_messages_key="history"
)

response=chat_with_history.invoke({"user_input":"我是小明"},{"configurable":{"session_id":"user_001"}})
print(response)