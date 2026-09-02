#从langchain包中的chat_models模块中导入init_chat_model函数
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

#创建一个OpenAI的实例
#OpenAI()
#直接使用的OpenAI的chat模型
#ChatOpenAI()
client = ChatOpenAI(
    model="qwen3.8-max"
)
#指定的模型供应商是OpenAI和ChatAI是一致的
#init_chat_model()

#模型不同，支持的SDK不同

response = client.invoke("你是谁?")

print(response.content)