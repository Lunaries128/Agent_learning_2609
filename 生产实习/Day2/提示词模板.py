import dotenv
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from rich import print as rprint
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import  ChatOpenAI

dotenv.load_dotenv()

client=ChatOpenAI(
    model="qwen3.8-max"
)

#任务1：数据提取
extract_prompt=ChatPromptTemplate.from_messages([
    {"role": "system", "content": "你是一个数据提取AI助手，信息以JSON格式返回"},
    {"role": "user", "content": "姓名：{name},年龄：{age}，性别：{gender}"}
])
extract_chain=extract_prompt|client|StrOutputParser()

#任务2：通用问答
qa_prompt = ChatPromptTemplate.from_messages([
    {"role": "system", "content": "你是一个乐于助人的AI助手"},
    {"role": "user", "content": "{question}"}
])
qa_chain=qa_prompt|client| StrOutputParser()

#链式结构 从左到右执行
#第一个是提示词  第二个是模型 第三个是结果格式化
#chain=prompt|client|StrOutputParser() (JsonOutputParser ,也可以写StrOutputParser)

response=extract_chain.invoke({"name":"张无忌","age":22,"gender":"男"})
response1=extract_chain.invoke({"name":"张三丰","age":25,"gender":"女"})
response2=qa_chain.invoke({"question":"1+1=?"})
response3=qa_chain.invoke({"question":"2+2=?"})
rprint(response)
rprint(response1)
rprint(response2)
rprint(response3)