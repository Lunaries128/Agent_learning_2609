import json

from langchain_openai import ChatOpenAI
from pyexpat.errors import messages
from rich import print as rprint
import dotenv

dotenv.load_dotenv()


"""
client = ChatOpenAI(
    model="qwem3.8-max"
)

client = init_chat_model(
    model="qwem3.8-max",
    model_provider="openai"
)
"""

#role=system 属于当前对话的规则，总体定义（一轮对话只能存在一个system）
#用messages列表模拟多轮对话，通过累积上下文让模型理解对话规则

#消息的三种角色
#system：系统指令，相当于给模型定规矩。比如"你是一个数据提取助手，回复用JSON格式"。一轮对话通常只设一次，放在列表最前面
#user：用户说的话
#assistant：模型之前的回复（多轮对话时，模型会自动记住）

messages=[{"role":"system","content":"你是一个用户数据提取的助手，用户的消息都以JSON格式返回"}]

client = ChatOpenAI(
    model="qwem3.8-max",
)


#invoke()可以是一个字符串也可以是一个列表
#请以标准的JSON格式给我返回数据 目前只能在response1上起作用
messages.append({"role":"user","content":"我叫张无忌，年龄25岁，性别为男"})
response=client.invoke(messages)

#response2没有如（请以标准格式的JSON格式给我返回数据） 以原始的结果格式返回
messages.append({"role":"user","content":"姓名：张三丰，年龄30，性别男"})
response1=client.invoke(messages)

#如果当前是一个对论对话（对论对话有一定的规则）


#HumanMessage()模型封装用户的消息{”role":"user","content":""} 追自动转换成HumanMessage

#模型返回的封装成一个AImessage的对象
rprint(type(response))
rprint(response.content)
