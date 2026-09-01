#导入openai的库以及OpenAI这个类
from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

#定义了一个变量（client）接收了一个OpenAI的对象
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

#chat聊天模型 创建一次会话（和指定模型交互）
completion=client.chat.completions.create(
    #指定模型名称，基于百炼平台，后续切模型只需要更改model名称
    model="qwen3.8-max",
    #消息列表{} 字典类型（）元组 []列表 {}字典（key：value）
    #role角色 user用户 content内容
    messages=[{"role":"user","content":"你可以解决什么问题"}]
)
print(completion.choices[0].message.content)

#推荐使用平台以及OpenAI
"""
注意：
如果修改了环境变量是在启动了pycharm之后的动作，那么修改完环境变量必须重启pycharm
（pycharm会在启动的时候重新加载一次环境变量）
"""