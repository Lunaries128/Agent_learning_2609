import os
import dotenv
#把当前.env里面的配置信息导入到环境中
dotenv.load_dotenv()

#os.getenv
key=os.getenv("OPENAI_API_KEY")
url=os.getenv("OPENAI_API_BASE")