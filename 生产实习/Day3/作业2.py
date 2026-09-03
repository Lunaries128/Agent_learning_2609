import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import dotenv

dotenv.load_dotenv()

chat_model=ChatOpenAI(
    model="qwen3.7-max",
    streaming=True
)

#page_title指定当前页面的标题 layout是当前页面的布局（wide宽屏布局centreed窄屏布局）
st.set_page_config(
    page_title="Chat Robot",
    page_icon="🤯",
    layout="wide"
)

#短期记忆+压缩摘要
def compress_history(messages):

    if len(messages) > 7:
        #分离旧消息（用于压缩）和新消息（短期记忆）
        history_messages = messages[:len(messages) -6]
        recent_messages = messages[len(messages) -6:]

        #格式化旧消息为纯文本
        old_messages = ""
        for mess in history_messages:
            role="user" if mess.type == "human" else "assistant"
            old_messages += f"{role}:" + mess.content + "\n"

        #调用LLM生成摘要
        llm = ChatOpenAI(model="qwen3.7-max", temperature=0.3, max_tokens=200)
        compress_messages = [
            SystemMessage(
                content="你是一个文本摘要助手，请把下面对话的历史消息压缩成一段简短的前情提要（不超过50个字），保留关键信息。只输出摘要内容。"),
            HumanMessage(content=old_messages)
        ]
        try:
            compress_response=llm.invoke(compress_messages)
            # 构建新的消息历史：[摘要]+[短期记忆]
            new_history=[SystemMessage(content=f"【前情提要】{compress_response.content}")]
            new_history.extend(recent_messages)
            return new_history
        except Exception as e:
            st.error(f"生成摘要时出错: {e}")
            # 出错时返回原消息，保证程序不崩溃
            return messages
    return messages

#判断当前streamlit的session_state内部是否存在message这个key
#第一次一定是不存在的，所以第一次会创建messages这个key值，而且让key绑定了空的列表
if "messages" not in st.session_state:
     st.session_state.messages=[]

#显示历史消息
#如果没有任何消息，显示标题
if not st.session_state.messages:
    st.markdown(
        "<h1 align='center'>Chat Robot</h1>",
        unsafe_allow_html=True
    )

#循环遍历并显示所有历史消息
for message in st.session_state.messages:
    if isinstance(message, SystemMessage):
        #将摘要放在一个可折叠的框里，保持界面整洁
        with st.expander("查看对话摘要"):
            st.info(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("human",avatar=":material/face:"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("AI",avatar=":material/smart_toy:"):
            st.write(message.content)

#用户输入
if prompt:=(
        st.chat_input("输入你的内容")):
    #添加并显示用户消息
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("human",avatar=":material/face:"):
        st.write(prompt)

    #获取并显示AI流式回复
    with st.chat_message("AI",avatar=":material/smart_toy:"):
        #将整个消息历史（包含摘要和短期记忆）传给模型
        ai_response_content = st.write_stream(chat_model.stream(st.session_state.messages))

    #添加AI消息到历史
    st.session_state.messages.append(AIMessage(content=ai_response_content))

    #执行后台压缩
    #在完整回复后，更新消息历史
    st.session_state.messages = compress_history(st.session_state.messages)

    #重绘页面以反映变化
    st.rerun()