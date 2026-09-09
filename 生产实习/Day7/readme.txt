1.安装库
pip install langchain langchain-openai dotenv pandas matplotlib fastapi streamlit uvicorn requests matplotlib pydantic

启动:
2.启动后端程序 FastAPI
uvicorn api:app --reload --port 8000

3.启动前端程序 streamlit
streamlit run C:\Users\12403\Desktop\PythonProject\生产实习\Day7\app.py

4.测试问题
从上海去杭州玩3天，两个人，
预算5000元，喜欢自然和人文，
不想太累，请生成每日行程、预算表和地图。

生成方案后继续输入：

第二天太累了，减少一个景点，
但必须保留西湖，预算不能增加。

5.项目说明
当前天气、景点、路线和价格使用课程演示模拟数据。
系统暂不提供真实预订和支付功能。