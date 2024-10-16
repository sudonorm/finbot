import requests
import os
from dotenv import load_dotenv
from typing import Union

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY", False)
FMP_API_STEM = os.getenv("FMP_API_STEMv3", False)


if not FMP_API_KEY:
    raise ValueError(
        "An FMP API key is needed to run this script. Please add one to the .env file using the variable name 'FMP_API_KEY' and try again"
    )

if not FMP_API_STEM:
    raise ValueError(
        "Please add the FMP_API_STEM variable and appropriate URL to the .env file using the variable name 'FMP_API_STEM' and try again"
    )


class CompanyMetrics:
    """This class contains methods used to pull company metrics from the FMP API"""

    def get_company_details(self, ticker: str) -> Union[str, bool]:
        """This function is used to pull company profile information from the FMP API

        Args:
            ticker (str): the ticker of the company e.g. MSFT

        Returns:
            Union[str, bool]: we either return a pipe (|) separated string of the company's information if we find one or
              we return False if we cannot find anything
        """

        company_profile_metrics = [
            "symbol",
            "price",
            "volAvg",
            "mktCap",
            "lastDiv",
            "changes",
            "companyName",
            "currency",
            "cik",
            "isin",
            "cusip",
            "exchange",
            "exchangeShortName",
            "industry",
            "website",
            "description",
            "ceo",
            "sector",
            "country",
            "fullTimeEmployees",
            "phone",
            "address",
            "city",
            "state",
            "zip",
            "ipoDate",
            "isEtf",
            "isActivelyTrading",
            "isAdr",
            "isFund",
        ]

        result, executives, company_details = False, False, False

        FMP_API_ENDPOINT = "profile"
        FMP_API_STEM = os.getenv("FMP_API_STEMv3", False)

        ### ticker information needed
        ### here we pull the company profile details
        company_profile_response = requests.get(
            url=f'{FMP_API_STEM}{FMP_API_ENDPOINT}/{ticker}{"?"}{"apikey="}{FMP_API_KEY}'
        )

        if (
            company_profile_response.status_code in [200, 201]
            and len(company_profile_response.json()) > 0
        ):
            result = "|".join(
                f"{key}{':'}{value}"
                for key, value in company_profile_response.json()[0].items()
                if key in company_profile_metrics
            )

        FMP_API_ENDPOINT = "key-executives"
        FMP_API_STEM = os.getenv("FMP_API_STEMv3", False)

        ### ticker information needed
        ### here we pull details about the company's executives
        company_executives = requests.get(
            url=f'{FMP_API_STEM}{FMP_API_ENDPOINT}/{ticker}{"?"}{"apikey="}{FMP_API_KEY}'
        )

        if (
            company_executives.status_code in [200, 201]
            and len(company_executives.json()) > 0
        ):
            executives = "|".join(
                x
                for x in [
                    f'{k.get("name")}{": "}{k.get("title")}'
                    for k in company_executives.json()
                ]
            )

        if result and executives:
            company_details = f'{result}{"|"}{executives}'
        elif result and not executives:
            company_details = result
        elif not result and executives:
            company_details = executives

        return company_details

    def get_company_earnings_transcript(self, ticker: str) -> Union[str, bool]:
        """This function can be used to pull a company's earnings transcript from the FMP API

        Args:
            ticker (str): the ticker of the company e.g. AAPL

        Returns:
            Union[str, bool]: we either return the company's earnings transcript if we find one
            or we return False if we cannot find it
        """

        earning_call_transcript = False

        FMP_API_ENDPOINT = "earning_call_transcript"
        FMP_API_STEM = os.getenv("FMP_API_STEMv4", False)

        ### ticker information needed
        ### here, we pull the date of the last earnings call. This can potentially be extended to pull the last x dates
        last_earning_call = requests.get(
            url=f'{FMP_API_STEM}{FMP_API_ENDPOINT}{"?symbol="}{ticker}{"&"}{"apikey="}{FMP_API_KEY}'
        )

        if (
            last_earning_call.status_code in [200, 201]
            and len(last_earning_call.json()) > 0
        ):
            last_earning_call_month = last_earning_call.json()[0][0]
            last_earning_call_year = last_earning_call.json()[0][1]

            FMP_API_ENDPOINT = "earning_call_transcript"
            FMP_API_STEM = os.getenv("FMP_API_STEMv3", False)

            ### ticker information needed
            earning_call_summary = requests.get(
                url=f'{FMP_API_STEM}{FMP_API_ENDPOINT}/{ticker}{"?year="}{last_earning_call_year}{"&quarter="}{last_earning_call_month}{"&"}{"apikey="}{FMP_API_KEY}'
            )

            if (
                earning_call_summary.status_code in [200, 201]
                and len(earning_call_summary.json()) > 0
            ):
                earning_call_transcript = earning_call_summary.json()[0].get("content")

        return earning_call_transcript
