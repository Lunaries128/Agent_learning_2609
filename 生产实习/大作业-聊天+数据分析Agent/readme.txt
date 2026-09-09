1.安装库
pip install langchain langchain-openai dotenv pandas matplotlib fastapi streamlit

启动:
1.启动后端程序 FastAPI
uvicorn api:app --reload --port 8000
2.启动前端程序 streamlit
streamlit run C:\Users\12403\Desktop\PythonProject\生产实习\大作业-聊天+数据分析Agent\app.py