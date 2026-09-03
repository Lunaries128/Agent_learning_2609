import streamlit as st
from langchain_openai import ChatOpenAI
import dotenv

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.7-max",
    streaming=True
)

#######
# if "messages" not in st.session_state:
#     st.session_state.messages=[]
#
# if len(st.session_state.messages)==0:
#     st.markdown("""
#     <h1 align="center">Chat Robot</h1>
#     """, unsafe_allow_html=True)
#
# for message in st.session_state.messages:
#     if message["role"] == "user":
#         with st.chat_message("human",avatar=":material/face:"):  #human相当于角色
#             st.write(message["content"])
#     elif message["role"] == "assitant":
#         with st.chat_message("AI",avatar=":material/smart_toy:"):
#             st.write(message["content"])
#
# prompt=st.chat_input("输入你的内容")
#
# if prompt:
#     st.session_state.messages.append({"role":"user","content":prompt})
#     user_message=st.chat_message("human",avatar=":material/face:")
#     user_message.write(prompt)
#
#     with st.chat_message("AI",avatar=":material/smart_toy:"):
#         response=chat_model.stream(prompt)
#         ai_message=st.write_stream(response)
#         st.session_state.messages.append({"role":"assistant","content":ai_message})
#####

#page_title指定当前页面的标题 layout是当前页面的布局（wide宽屏布局centreed窄屏布局）
st.set_page_config(
    page_title="Chat Robot",
    page_icon="🤯",
    layout="wide"
)


#判断当前streamlit的session_state内部是否存在message这个key
#第一次一定是不存在的，所以第一次会创建messages这个key值，而且让key绑定了空的列表
if "messages" not in st.session_state:
     st.session_state.messages=[]

#获取用户的输入
prompt=st.chat_input("输入你的内容")

#判断输入是否有内容
if prompt:
    #把用户输入的内容存储到streamlit的session_state的message列表中
    st.session_state.messages.append({"role":"user","content":prompt})

#判断streamlit的session_state是否存在消息
#not 如果streamlit的session_state存在消息 则不满足条件
if not st.session_state.messages:
    st.markdown("""
        <h1 align="center">Chat Robot</h1>
        """, unsafe_allow_html=True)

#循环遍历streamlit的session_state的messages把历史消息全部显示
for message in st.session_state.messages:
   if message["role"] == "user":
         with st.chat_message("human",avatar=":material/face:"):  #human相当于角色
             st.write(message["content"])
   elif message["role"] == "assitant":
         with st.chat_message("AI",avatar=":material/smart_toy:"):
             st.write(message["content"])

#和大模型交互，把模型返回的结果按照流式的方式输出到AI_message这个组件上
if prompt:
    with st.chat_message("AI",avatar=":material/smart_toy:"):
        ai_message=st.write_stream(chat_model.stream(prompt))
    st.session_state.messages.append({"role":"user","content":ai_message})