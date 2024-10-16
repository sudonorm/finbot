import dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

# from langchain_community.document_loaders import JSONLoader
# from langchain_openai import OpenAIEmbeddings
# import ast
# from langchain_chroma import Chroma

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables import RunnableParallel

from pydantic import BaseModel, Field
import sys
import os

home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
home_dir_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

if home_dir not in sys.path:
    sys.path.append(home_dir)
if home_dir_parent not in sys.path:
    sys.path.append(home_dir_parent)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from core.config import settings

dotenv.load_dotenv()

chat_model = ChatOpenAI(
    model=os.getenv("BOT_MODEL"), temperature=0, api_key=settings.API_KEY
)


######## Chains ############


### Response Class #####
class TickerResponse(BaseModel):
    ticker: str = Field(description="ticker of a company")


### prompt system template. This is the main instruction
ticker_system_template_str = """You are a financial assistant. Given a user query, extract and return the company's ticker symbol if mentioned directly. If the query includes a company name instead of a ticker, check for the ticker for the company and return the ticker.
Only return the ticker. 
User Query: "{user_query}"
"""

system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(template=ticker_system_template_str)
)

human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["user_query"], template="{user_query}")
)

messages = [system_prompt, human_prompt]

### create chat prompt template from system and human prompt
prompt_template = ChatPromptTemplate(
    input_variables=["user_query"],
    messages=messages,
)

### format output as structured model response
structured_llm_model = chat_model.with_structured_output(TickerResponse)

### initialize chain
chain_from_docs = prompt_template | structured_llm_model

### assign runnable
chain_with_source = RunnableParallel({"user_query": RunnablePassthrough()}).assign(
    answer=chain_from_docs
)
