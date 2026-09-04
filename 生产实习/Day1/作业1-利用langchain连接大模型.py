#从langchain包中的chat_models模块中导入init_chat_model函数
from langchain.chat_models import init_chat_model

client = init_chat_model(
    model_provider="openai",
    model="qwen3.8-max",
    base_url="https://ws-rpapg7qma074szzh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    api_key="sk-ws-H.PMMHDXL.KGCU.MEQCID38e_dm9U2EJP1o0A7RIUih2JphdfGdOMZGyQQkXyVKAiBC8d0DAxeII4Xgc2DS6_X5SgaQXvYqeySavAbtfHlQJA",

    extra_body={
        "enable_thinking": True
    }
)

response = client.invoke("你是谁？")

print(response)
