import chromadb
#指定嵌入模型 需要导入函数
from chromadb.utils import embedding_functions

#指定嵌入模型
ef=embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5",
)

#初始化客户端（持久化模式）
#path参数指定当前的数据文件路径（本地存储的数据文件地址），chromadb会在当前的工程目录下自动的创建一个my_chroma_dbb的文件夹
client_db=chromadb.PersistentClient(path="./my_chroma_db")

#创建或者获取一个集合（collection）类似于在仓库中创建一个货架
#get_or_create_collection() 如果指定的collection在当前chromaDB中存在就get（获得），不存在就create（创建）
collection=client_db.get_or_create_collection(name="chat_memory",embedding_function=ef)

#存入数据（是存入到某个“货架”collection内部）collection.add()来存入数据
#需要传入三个东西：唯一的ID，原始的文本（数据），元数据（metadata 标签）
#ids=[] 列表（每个数据唯一的标识）相当于当前数据的身份证号码
#documents=[] 原始的数据（chromadb会把当前文本数据转换成向量 后台自动调用向量模型）
#metadatas=[] 给每条记录（数据）打上标签，方便以后也可以通过metadata来过滤数据
collection.add(
    ids=['mem_001','mem_002','mem_003'],
    documents=[
        "我叫小明，是一名大学生，正在学习python",
        "我最喜欢吃的水果是苹果和香蕉",
        "我未来的目标是成为一名AI算法工程师"
    ],
    metadatas=[
        {"type":"个人信息","time":"2026-07"},
        {"type":"偏好","time":"2025-10"},
        {"type":"职业","time":"2026-09"},
    ]
)

print("数据存入成功")

#语义搜索
#用一句自然语言搜索，chromadb会自动把问题（搜索的数据）也转换成向量，并在指定的collection上查找相似的记录
#collection.query()目前调用query()函数的对象是collection，即当前检索会在指定的collection上检索
#参数：
#1.query_texts这个参数是一个列表的类型（给多个query）
#2.n_result连锁返回的结果的条数
result=collection.query(
    query_texts=["我的职业梦想是什么？"],
    n_results=3
)

#查看检索的结果
#result是一个字典的类型，包含ids、documents、distance（距离）等信息
for item in range(len(result["ids"][0])):
    doc=result["documents"][0][item]
    dist=result["distances"][0][item]
    print(f"内容：{doc}，（相似的距离：{dist:4f}）")







