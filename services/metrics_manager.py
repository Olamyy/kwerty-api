import calendar
import dataclasses
from datetime import datetime
from pprint import pprint
from typing import Dict, List
import pandas

from services.prompt_manager import PromptManager


@dataclasses.dataclass
class CountryResultManager:
    summary: str = None
    openai_extract: Dict = None
    pandas_extract: Dict = None
    is_valid: bool = None


class MetricsManager:
    def __init__(self, country_data: List[Dict[str, List[Dict[str, str]]]]):
        self.country_data = country_data
        self.dataset = pandas.read_csv('cleaned_data.csv')
        self.columns = set(self.dataset.columns.to_list())
        self.countries = set(self.dataset['Country'].to_list())
        self.prompter = PromptManager

    def process_metrics(self):
        result = []
        for country_information in self.country_data:
            country_extraction = []
            try:
                country = country_information['country']
                if country in self.countries:
                    metrics = country_information['metrics']
                    for metric in metrics:
                        query_string, metric_result = self.build_and_run_metric(country, metric)
                        if len(metric_result) == 1:
                            extracted_country = CountryResultManager(
                                openai_extract=metric,
                                pandas_extract=self.extract_data_from_df(metric, metric_result),
                                is_valid=True
                            )
                            as_dict = dataclasses.asdict(extracted_country)
                            del as_dict['pandas_extract']
                            generated_summary = self.prompter.generate_summary(as_dict)
                            extracted_country.summary = generated_summary
                            country_extraction.append(
                                extracted_country
                            )
                        else:
                            extracted_country = CountryResultManager(
                                openai_extract=metric,
                                pandas_extract=self.extract_data_from_df(metric, metric_result,
                                                                         action="get_actual", country=country),
                                is_valid=False
                            )
                            as_dict = dataclasses.asdict(extracted_country)
                            del as_dict['pandas_extract']
                            generated_summary = self.prompter.generate_summary(as_dict)
                            extracted_country.summary = generated_summary
                            country_extraction.append(
                                extracted_country
                            )

                result.append(
                    {
                        "country": country,
                        "result": country_extraction
                    }
                )
            except TypeError:
                print(
                    {
                        "status": "error",
                        "extract": country_information,
                        "country_data": self.country_data
                    }
                )
        return result

    def build_and_run_metric(self, country, metric):
        month_year = self.build_month_year_format(metric['month'], metric['year'])
        query_string = f"""Country=='{country}' and Indicator=='{metric['metric']}'"""
        if month_year in self.columns:
            query_string = f"{query_string} and {month_year}=='{metric['value']}'"
        print(query_string)
        return query_string, self.dataset.query(query_string)

    @staticmethod
    def build_month_year_format(month, year):
        if month in [None, 'None', 'NA', 'N/A'] or not year or len(month) < 3:
            today = datetime.now()
            return f"{calendar.month_abbr[3]}_{str(today.year)[2:]}"
        return f"{str(month)[:3]}_{str(year)[2:]}"

    def get_actual(self, country, metric):
        month_year = self.build_month_year_format(metric['month'], metric['year'])
        query_string = f"""Country=='{country}' and Indicator=='{metric['metric']}'"""
        query = self.dataset.query(query_string)
        query_with_month = query.get(month_year)
        return query, query_with_month

    def extract_data_from_df(self, metric, metric_result, action=None, country=None):
        value = "NOT_AVAILABLE"
        if action == "get_actual":
            query, query_with_month = self.get_actual(country, metric)
            country_information = query.to_dict(orient="records")[0]
            # if query_with_month.empty or len(query_with_month) > 0:

            if not query_with_month.empty or len(query_with_month) > 0:
                pprint({
                    "query": query,
                    "query_with_month": query_with_month
                })
                value = query_with_month.values[0]
        else:
            country_information = metric_result.to_dict(orient="records")[0]
        result = {
            "country": country_information['Country'],
            "Indicator": country_information['Indicator'],
            "Source": country_information['Source'],
            "Link": country_information['Link'],
            "CurrencyCode": country_information['CurrencyCode'],
            "Unit": country_information['Unit'],
            "Category": country_information['Category'],
            "Frequency": country_information['Frequency'],
            "Note": country_information['Note'],
            "Tag": country_information['Tag'],
            "CountryCode": country_information['CountryCode'],
            "IndicatorDefinition": country_information["IndicatorDefinition"],
        }
        month_year = self.build_month_year_format(metric['month'], metric['year'])
        result['value'] = country_information[month_year] if value == "NOT_AVAILABLE" else value
        result = self.serialize_result(result)
        return result

    @staticmethod
    def serialize_result(result):
        for key, value in result.items():
            try:
                if pandas.isna(value):
                    result[key] = None
            except ValueError:
                if value.empty:
                    result[key] = None
        return result
