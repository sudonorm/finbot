import dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

# from langchain_community.document_loaders import JSONLoader
# from langchain_openai import OpenAIEmbeddings
# import ast
# from langchain_chroma import Chroma

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.runnables import RunnableParallel

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

### prompt system template. This is the main instruction

system_template_str = """
You are an intelligent assistant that provides answers based solely on the provided context. 
Do not use any external information or your own knowledge beyond the given context. 

### Context:
---
{context}
---

### User Question:
{user_query}

### Answer:
"""

system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["context"], template=system_template_str)
)

human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["user_query"], template="{user_query}")
)

messages = [system_prompt, human_prompt]

### create chat prompt template from system and human prompt
prompt_template = ChatPromptTemplate(
    input_variables=["context", "user_query"],
    messages=messages,
)

### format output as string instead of AIMessage
output_parser = StrOutputParser()

### initialize chain
chain_from_docs = prompt_template | chat_model | output_parser

### assign runnables
chain_with_source = RunnableParallel(
    {"context": RunnablePassthrough(), "user_query": RunnablePassthrough()}
).assign(answer=chain_from_docs)
