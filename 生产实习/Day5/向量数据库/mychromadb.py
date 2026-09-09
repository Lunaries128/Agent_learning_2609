import chromadb
from mymodels import chat_model
from chromadb.utils import embedding_functions
import uuid

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="../embeddingmodel/bge-small-zh-v1.5",
)

chromadb_client = chromadb.PersistentClient("./my_memory_db")

memory_collection = chromadb_client.get_or_create_collection("memory_collection",embedding_function=ef)

# 存储消息
def extract_and_store_memory(user_input,ai_reply):
    """
    从对话中提取值得长期存储的信息，存入到数据库中
    -- 不是每句话都值得存储(例如：你好，谢谢之类的信息是不用存储的)
    -- 让大模型先判断当前的消息是否需要存储 如果有需要存储的再存储到数据库中
    :param user_input: 用户的消息
    :param ai_reply: 模型回复的消息
    :return:
    """
    messages = [{"role":"system","content":"""
        你是一个信息提取的助手，请判断以下的对话中是否包含需要记录的信息(例如:姓名、职业、喜好、目标、经历等)，如果包含请提取出来，
        用一句话概括，格式为：用户[信息内容]。如果不包含任何值得记录的信息，请只回复：无。只输出提取结果或者"无",不要加任何解释。
    """},
                {"role":"user","content":f"用户说:{user_input}\n助手说:{ai_reply}"},
    ]

    extract = chat_model.invoke(messages)
    if extract.content == "无" or len(extract.content) < 5:
        return

    memory_id = str(uuid.uuid4())

    memory_collection.add(
        ids=memory_id,
        metadatas=[{"source":"chat"}],
        documents=[extract.content],
    )

# 检索消息
def search_long_term_memory(query_text):
    """
    从向量数据库中检索与当前问题相关的长期记忆
    -- 把用户的问题转换成向量
    -- 在数据库中查找语义最相似的记录
    -- 返回最相关的2条记忆
    :param query_text: 用户的问题
    :return: 与用户问题相关的长期记忆里面的2条记录
    """
    # memory_collection(长期记忆的集合) count() 记录数
    if memory_collection.count() == 0:
        return ""

    results = memory_collection.query(
        query_texts=[query_text],
        n_results=2,
    )

    memories = results['documents'][0]

    if not memories:
        return ""

    memory_text = "\n".join([f"- {m}" for m in memories])

    return memory_text