import calendar
import dataclasses
from datetime import datetime
from typing import Dict, List, Set

import pandas
from pydantic import BaseModel

from config import ERROR_REASONS
from services import STARTUP_OBJECTS

MONTH_VARIANTS = [None, "None", "NA", "N/A"]


class CountryMetric(BaseModel):
    metric_year: int
    metric_name: str
    metric_month: str
    metric_value: str
    metric_source: str


@dataclasses.dataclass
class ExtractionError:
    error: bool
    error_reason: str


@dataclasses.dataclass
class CountryResultManager:
    openai_extract: CountryMetric = None
    kwerty_validation: Dict = None
    is_valid: bool = None
    error: ExtractionError = None


@dataclasses.dataclass
class QueryValidity:
    base_query_is_valid: bool = False
    metric_value_is_valid: bool = False


class PandasQuery:
    def __init__(
        self,
        country_name: str,
        metric: CountryMetric,
        validation_data: pandas.DataFrame,
        columns: Set[str],
    ):
        self.country_name = country_name
        self.metric = metric
        self.validation_data = validation_data
        self.columns = columns
        self.queries = {}
        self.query_validity = QueryValidity()

    def build_query_string(self, month_year: str):
        query_string = f"""Country=='{self.country_name}' and Indicator=='{self.metric.metric_name}'"""
        self.queries["validation_query"] = {"base_query_string": query_string}
        return

    @staticmethod
    def build_month_year_format(month, year):
        if month in MONTH_VARIANTS or not year or len(month) < 3:
            today = datetime.now()
            return f"{calendar.month_abbr[3]}_{str(today.year)[2:]}"
        return f"{str(month)[:3]}_{str(year)[2:]}"

    def run_query(self):
        month_year = self.build_month_year_format(
            self.metric.metric_month, self.metric.metric_year
        )
        self.build_query_string(month_year)
        base_query = self.queries["validation_query"]["base_query_string"]
        base_query_result = self.validation_data.query(base_query)
        if len(base_query_result) == 1:
            self.query_validity.base_query_is_valid = True
            query_result_dict = base_query_result.to_dict(orient="records")[0]
            if query_result_dict[month_year] == self.metric.metric_value:
                self.query_validity.metric_value_is_valid = True
            self.queries["validation_query"]["query_result"] = query_result_dict

        return

    def get_validated_country_data(self):
        country_information = self.queries["validation_query"]["query_result"]
        country_data = {
            "country": country_information["Country"],
            "indicator": country_information["Indicator"],
            "source": country_information["Source"],
            "link": country_information["Link"],
            "currency_code": country_information["CurrencyCode"],
            "unit": country_information["Unit"],
            "category": country_information["Category"],
            "frequency": country_information["Frequency"],
            "note": country_information["Note"],
            "tag": country_information["Tag"],
            "country_code": country_information["CountryCode"],
            "indicator_definition": country_information["IndicatorDefinition"],
            "value": None,
        }
        month_year = self.build_month_year_format(
            self.metric.metric_month, self.metric.metric_year
        )
        country_data["value"] = country_information[month_year]
        return self.serialize_result(country_data)

    @staticmethod
    def serialize_result(country_data):
        for key, value in country_data.items():
            try:
                if pandas.isna(value):
                    country_data[key] = None
            except ValueError:
                if value.empty:
                    country_data[key] = None
        return country_data


class MetricsManager:
    def __init__(self, country_data: List[Dict]):
        self.country_data = country_data
        self.validation_data: pandas.DataFrame = STARTUP_OBJECTS["validation_data"]
        self.columns = self.get_columns()
        self.result = []

    def process_metrics(self):
        country_names = self.get_supported_countries()
        for country_information in self.country_data:
            extracted_information = []
            country_name = country_information["country"]
            if country_name not in country_names:
                extracted_information.append(
                    CountryResultManager(
                        error=ExtractionError(
                            error=True,
                            error_reason=ERROR_REASONS["CountryNotSupported"],
                        )
                    )
                )
            else:
                metrics = country_information["country_metrics"]
                if not metrics:
                    extracted_information.append(
                        CountryResultManager(
                            error=ExtractionError(
                                error=True, error_reason=ERROR_REASONS["NoMetricsFound"]
                            )
                        )
                    )
                else:
                    metrics = [CountryMetric(**metric) for metric in metrics]
                    for metric in metrics:
                        pandas_query_handler = PandasQuery(
                            country_name=country_name,
                            metric=metric,
                            validation_data=self.validation_data,
                            columns=self.columns,
                        )
                        pandas_query_handler.run_query()
                        extracted_information.append(
                            CountryResultManager(
                                openai_extract=metric,
                                kwerty_validation=pandas_query_handler.get_validated_country_data(),
                                is_valid=pandas_query_handler.query_validity.metric_value_is_valid,
                            )
                        )

            self.result.append(
                {"country": country_name, "result": extracted_information}
            )

        return self.result

    def get_supported_countries(self):
        return self.validation_data["Country"].to_list()

    def get_columns(self):
        return set(self.validation_data.columns.to_list())
