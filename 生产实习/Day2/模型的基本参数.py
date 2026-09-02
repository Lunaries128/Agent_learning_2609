from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

#流式输出更接近LLM的工作流程
#LLM（大语言模型）概率，预测下一个token
#OpenAI的参数
#model指定连接的大模型的名称
#temperature发散度（0-2.0，数值越大发散程度越高；数值越小，结果越确定）
#max_tokens限定当前对话的总token数量
#timeout连接模型过期时间
client = ChatOpenAI(
    model="qwen3.8-max",
    temperature=1.7,
    max_tokens=10000,
    timeout=5000,
    stream_usage=True,
)

response=client.invoke("翻译：The early brid catches thee worm")
print(response.content)