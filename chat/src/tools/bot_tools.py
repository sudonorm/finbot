import sys
import os

home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
home_dir_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

if home_dir not in sys.path:
    sys.path.append(home_dir)
if home_dir_parent not in sys.path:
    sys.path.append(home_dir_parent)

from utils.get_news import News
from chains import summary_chain, news_chain, context_response_chain, ticker_chain
from utils.company_metrics import CompanyMetrics

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import datetime
import dotenv
from core.config import settings

dotenv.load_dotenv()

model = ChatOpenAI(
    model=os.getenv("BOT_MODEL"), temperature=0, api_key=settings.API_KEY
)

system_template_str = """Think step-by-step about the things that a finance bot will be able to answer. You can answer questions about finance, info about companies, recent news about people or companies.
    If a customer asks a question outside the domain of those things mentioned above or which cannot be answered using any tool,
    apologize to the customer, inform them kindly that you cannot answer their question and request that they ask you questions related to the things mentioned above.   
    """


def docstring_parameter(*sub):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj

    return dec


# Define the tools for the agent to use


@tool
def apologize(query: str):
    """
    This tool is used to apologize to the customer when a question cannot be answered. Questiona outside of finance, info about companies, recent news about people or companies should not be answered
    """

    message_plc = [SystemMessage(content=system_template_str)] + [
        HumanMessage(content=query)
    ]
    response = model.invoke(message_plc)

    return response


@docstring_parameter(datetime.datetime.now().year)
@tool
def get_news_about_events(query: str):
    """
    This tool is used to answer questions regarding news which require browsing the internet about cpmpanies and/or people.
    It should be used when we want to know what was said about a company, profitability of the company, or about people and their opinion about topics.
    It can be used to answer news about past and recent events concerning people or companies because it can be used to browse the internet.
    Unless explicitly stated, it should search for the most recent news close to, or in, {0}
    """

    news = News()

    ### Here, we only get the first 5 articles
    articles = news.get_news_for_user_query(user_query=query)

    ### We summarize the articles, in case they are too long
    articles_summarized = summary_chain.chain_with_source.invoke(
        {"context": articles, "user_query": query}
    )

    ### Then we use the summary to answer the question posed by the user
    query_response = news_chain.chain_with_source.invoke(
        {"context": articles_summarized["answer"], "user_query": query}
    )

    return query_response


@tool
def get_company_earnings_transcript_from_api(query: str):
    """
    This tool is used to summarize an earnings call or conference call of a company from data pulled from an API.
    It should not be used when we want to know certain sentiments surrounding this earning call.
    It should not be used if the question requires that we browse the internet.
    """

    cmpny_metrics = CompanyMetrics()

    ### First, we try to get the ticker
    ticker_response = ticker_chain.chain_with_source.invoke({"user_query": query})

    # print("ticker response: ", ticker_response)

    ### Here, we only pull the earnings call for the ticker
    company_earnings_call_transcript = cmpny_metrics.get_company_earnings_transcript(
        ticker=ticker_response["answer"]["ticker"].strip()
    )

    # print("company_earnings_call_transcript: ", company_earnings_call_transcript)

    ### We summarize the earnings call
    earning_call_transcript_summary_response = summary_chain.chain_with_source.invoke(
        {"context": company_earnings_call_transcript, "user_query": query}
    )

    return earning_call_transcript_summary_response


@tool
def get_information_about_a_company(query: str):
    """
    This tool is used to pull certain metrics of a company such as CEO, market cap, current price, names of executives,
    location and other metrics that might be relevant to a publicly listed company.
    It should not be used if the question requires we browse the internet or pull an earnings call or conference call.
    """

    cmpny_metrics = CompanyMetrics()

    ### First, we try to get the ticker
    ticker_response = ticker_chain.chain_with_source.invoke({"user_query": query})

    # print("ticker response: ", ticker_response)

    ### Then we pull company information for the company using the ticker
    company_details = cmpny_metrics.get_company_details(
        ticker=ticker_response["answer"]["ticker"].strip()
    )

    # print("company_details", company_details)

    ### We use the details as context to answer the user's question
    cmpny_response = context_response_chain.chain_with_source.invoke(
        {"context": company_details, "user_query": query}
    )

    return cmpny_response


tools = [
    # apologize, ### this can be turned on, if we want to bot to reply users in a certain way when it cannot find information
    get_news_about_events,
    get_company_earnings_transcript_from_api,
    get_information_about_a_company,
]
