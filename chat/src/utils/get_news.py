import trafilatura
from duckduckgo_search import DDGS
from typing import Union


class News:
    """This class contains methods which can be used to browse the internet and pull news from different sources"""

    def get_article(self, url: str) -> Union[str, bool]:
        """This function used duckduckgo to query a website on which we have news we want to extract

        Args:
            url (str): the url of the website we want to fetch data from

        Returns:
            Union[str, bool]: we either return the text on the page, extracted using trafilatura,
            or False if we cannot find anything
        """

        ddg = DDGS()
        try:
            source = ddg._get_url(method="GET", url=url)
            source_text = trafilatura.extract(source)
            return source_text
        except:
            return False

    def get_news_for_user_query(
        self,
        user_query: str,
        timelimit: str = "y",
        backend: str = "html",
        max_results: int = 5,
    ) -> Union[str, bool]:
        """This function uses duckduckgo to search the internet to find articles matching the user's query.
           In this case, to browse the internet, we use the bakend 'html' and not the conventional 'api' backend
           Max results is capped at 5 by default, as the more articles it has to pull the slower it is due to the extraction of the text
           from these websites.

        Args:
            user_query (str): the question the user poses e.g. What is the current sentiment about AI?
            timelimit (str, optional): the time span within which we want to search. Defaults to "y". This means search the last year.
            backend (str, optional): the backend to use. Defaults to "html". The backend "api" can also be used, but it often does not have the recent news
            max_results (int, optional): the maximum number of results to return. Defaults to 5.

        Returns:
            Union[str, bool]: a string of news articles extracted from various websites.
        """

        news_articles = False

        ddg = DDGS()
        res = ddg.text(
            keywords=user_query,
            timelimit=timelimit,
            backend=backend,
            max_results=max_results,
        )

        if len(res) > 0:
            news_articles_lst = [self.get_article(source["href"]) for source in res]
            news_articles_lst = [x for x in news_articles_lst if x]

            if len(news_articles_lst) > 0:
                news_articles = ". ".join(x for x in news_articles_lst if x)

        return news_articles
