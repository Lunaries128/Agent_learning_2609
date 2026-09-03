import streamlit as st
from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.7-max",
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
        with st.chat_message("human",avatar=":material/face:"):  #human相当于角色
            st.write(message["content"])
    elif message["role"] == "assitant":
        with st.chat_message("AI",avatar=":material/smart_toy:"):
            st.write(message["content"])

prompt=st.chat_input("输入你的内容")

if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    user_message=st.chat_message("human",avatar=":material/face:")
    user_message.write(prompt)

    ai_message=st.chat_message("AI",avatar=":material/smart_toy:")
    #response=chat_model.invoke(prompt)
    #response采用的是stream()，所以当前response就不是一次性返回所有回答
    response=chat_model.invoke(prompt)

    st.session_state.messages.append({"role":"assitant","content":response.content})
    ai_message.write(response.content)


