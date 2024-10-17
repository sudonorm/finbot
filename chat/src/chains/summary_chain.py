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

system_template_str = """TASK: TLDR. As a professional summarizer, create a concise and comprehensive summary of the provided text, be it an article, post, conversation, or passage, while adhering to these guidelines:
1. Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness.
2. Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects.
3. Rely strictly on the provided text, without including external information.
4. Format the summary in paragraph form for easy understanding.
5. Think step-by-step about what would be needed to answer the user's question {user_query}.
6. Utilize markdown to cleanly format your output. Example: Bolden key subject matter and potential areas that may need expanded information.

### Provided Text:
{context}

### Summary:
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
