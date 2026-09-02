#导入streamlit as 别名
import streamlit as st

#输出一个一级标题
st.title("hello world")
#输出普通文字
st.text("hello world")
#markdown（） 支持markdown语法结构
st.markdown("```hello world1```")

#输出代码格式
#st.code("public class Demo:{"
#       "   public static void main(String[] args) {"
#       "   }"
#       "}")

st.write("hello world2")

st.image(image="C:/Users/12403/Desktop/1.jpg",width=500)

st.button("按钮")

st.checkbox("复选框")

st.radio(label="男",options={"男"})

st.selectbox(label="学历",options=["博士","硕士","学士"])

st.number_input("电话")

st.sidebar.write("边侧栏")

st.sidebar.button("按钮1")

st.progress(value=50)