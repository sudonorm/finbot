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
from langchain.chains.combine_documents import create_stuff_documents_chain

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
You are an intelligent assistant that provides answers based solely on the provided news articles. 
Do not use any external information or your own knowledge beyond the given context. 
If the information is not available in the context, just infer what you can and respond based on the information available.

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


### initialize chain. We are using the stuff document chain here. This requires split documents using something like RecursiveCharacterTextSplitter as the context
chain_with_source = create_stuff_documents_chain(
    llm=chat_model, prompt=prompt_template, output_parser=output_parser
)
