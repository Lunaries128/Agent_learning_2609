from mychromadb import extract_and_store_memory, search_long_term_memory
from mymodels import chat_model

SYSTEM_PROMPT = """
你是一个聪明的AI助手，擅长用通俗易懂的比喻来挥发问题。回复控制到3--5局话。
重要:如果系统提示中包含了"用户的历史信息"，请在回答时自然的利用这些信息，让用户感受不到你记住了他。但不要刻意强调"我记得你说过...",要想朋友一样
自然的提及.
"""

while True:
    user_input = input("你(quit 退出):").strip()

    if user_input == "quit":
        print("再见!!!")
        break;

    # 每次把问题发给大模型之前先去一趟数据库，查找一下长期记忆里面是否存在与当前问题相关的历史记录
    long_term_memory = search_long_term_memory(user_input)
    current_system = SYSTEM_PROMPT
    if long_term_memory:
        current_system += long_term_memory
    messages = [{"role":"system","content":current_system},{"role":"user","content":user_input}]

    result = chat_model.invoke(messages)

    reply = result.content

    extract_and_store_memory(user_input, reply)

    print(f"AI:{reply}")


