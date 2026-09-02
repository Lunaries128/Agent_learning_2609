import streamlit as st
from langchain_openai import ChatOpenAI
import dotenv

num = 0

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.8-max"
)

st.markdown("""
<h1 align="center">聊天机器人</h1>
""",unsafe_allow_html=True)

st.write(f"第{num}次对话")

#获取用户的输入
prompt=st.chat_input("输入你的内容")

if prompt:
    user_message=st.chat_message("human")
    user_message.write(prompt)

    ai_message=st.chat_message("AI")
    response=chat_model.invoke(prompt)
    ai_message.write(response.content)

num += 1

# streamlit每次交互都会重新运行整个脚本
#如果不做处理，那么每次消息都会被消除掉
#streamlit的session_state(会话状态)


