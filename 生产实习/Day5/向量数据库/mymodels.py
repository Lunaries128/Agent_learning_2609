import os
from langchain.chat_models import init_chat_model
import dotenv

dotenv.load_dotenv()

chat_model = init_chat_model(
    model=os.getenv("CURRENT_MODEL_NAME"),
    model_provider=os.getenv("CURRENT_MODEL_PROVIDER"),
)



