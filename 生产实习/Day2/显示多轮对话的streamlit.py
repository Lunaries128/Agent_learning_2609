import streamlit as st
from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

with st.sidebar:
    st.header("设置")

    # 清空对话按钮
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

chat_model=ChatOpenAI(
    model="qwen3.8-max",
    stream_usage=True
)

if "messages" not in st.session_state:
    st.session_state.messages=[]

if len(st.session_state.messages)==0:
    st.markdown("""
    <h1 align="center">Chat Robot</h1>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("human"):
            st.write(message["content"])
    elif message["role"] == "assitant":
        with st.chat_message("AI"):
            st.write(message["content"])

prompt=st.chat_input("输入你的内容")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    user_message=st.chat_message("human")
    user_message.write(prompt)

    ai_message=st.chat_message("AI")
    response=chat_model.invoke(prompt)

    st.session_state.messages.append({"role":"assitant","content":response.content})
    ai_message.write(response.content)


