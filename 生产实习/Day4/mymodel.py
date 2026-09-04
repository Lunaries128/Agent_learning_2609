from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import dotenv

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system","你是一个聪明的的AI助手，请记简要的回答问题，不要啰嗦"),
    MessagesPlaceholder(variable_name="history"),
    ("human","{user_input}")
])

# 创建LLM
chat_model = init_chat_model(
    model_provider="deepseek",
    model="deepseek-v4-pro",
    streaming=True,
)

chain = prompt | chat_model
