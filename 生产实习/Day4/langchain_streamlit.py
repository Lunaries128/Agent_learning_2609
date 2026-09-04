import uuid

from myhistory import chat_with_history, get_session_history
import streamlit as st

st.set_page_config(page_title="聊天机器人",layout="wide")

user_input = st.chat_input("输入你的问题:")

if "session_titles" not in st.session_state:
    st.session_state.session_titles = {}
if "session_order" not in st.session_state:
    st.session_state.session_order = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.session_order.append(st.session_state.current_session_id)

with st.sidebar:
    if st.button("新建会话",use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_session_id = new_id
        st.session_state.session_order.append(new_id)
        st.rerun() # 手动让当前页面刷新

    st.markdown("""
        <font style='font-size:13px; color:#aaa;'>历史消息</font>
    """,unsafe_allow_html=True)

    for sid in reversed(st.session_state.session_order):
        title = st.session_state.session_titles.get(sid,"新对话")
        if st.button(title,key=sid,use_container_width=True,type="secondary"):
            st.session_state.current_session_id = sid
            st.rerun()

history_message = get_session_history(st.session_state.current_session_id)
for msg in history_message.messages:
    if msg.type == "human":
        with st.chat_message("human", avatar=":material/face:"):
            st.write(msg.content)
    else:
        with st.chat_message("AI", avatar=":material/smart_toy:"):
            st.write(msg.content)

if user_input:
    # 当前的用户的问题加入到历史消息中
    if not history_message.messages:
        st.session_state.session_titles[st.session_state.current_session_id] = user_input

    with st.chat_message("human", avatar=":material/face:"):
        st.write(user_input)

    with st.chat_message("ai",avatar=":material/smart_toy:"):
        response = chat_with_history.stream({"user_input":user_input},{"configurable":{"session_id":st.session_state.current_session_id}})
        st.write_stream(response)