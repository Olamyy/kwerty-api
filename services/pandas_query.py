import calendar
from datetime import datetime
from pprint import pprint
from typing import Set, Dict
import pandas
from pydantic import BaseModel, dataclasses

MONTH_VARIANTS = [None, "None", "NA", "N/A"]


@dataclasses.dataclass
class QueryValidity:
    base_query_string_is_valid: bool = False
    metric_value_is_valid: bool = False


class CountryMetric(BaseModel):
    metric_name: str
    metric_value: str
    metric_source: str = None
    metric_month: str = None
    metric_year: str = None


@dataclasses.dataclass
class Validity:
    is_valid: bool = None
    invalidity_reason: str = None


@dataclasses.dataclass
class Queries:
    base_query: str = None
    metric_query: str = None
    result: Dict = None


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
        self.queries = Queries()
        self.query_validity = QueryValidity()
        self.message = None
        self.validity = Validity()

    def _run_query(self, query):
        got_result = False
        result = None
        formatted_query = query
        while not got_result:
            query_result = self.validation_data.query(formatted_query)
            if not query_result.empty:
                got_result = True
                result = query_result
            formatted_query = "and".join(query.split("and")[:-1])

        if got_result:
            return result

    def build_base_query(self):
        query_string = f"country=='{self.country_name}'"
        if self.metric.metric_name:
            query_string = f"{query_string} and indicator.str.contains('{self.metric.metric_name.title()}')"
        if self.metric.metric_source:
            query_string = f"{query_string} and source.str.contains('{self.metric.metric_source}')"

        self.queries.base_query = query_string
        return query_string

    @staticmethod
    def build_month_year_format(month, year):
        if month in MONTH_VARIANTS or not year or len(month) < 3:
            today = datetime.now()
            return f"{calendar.month_abbr[3]}_{str(today.year)[2:]}"
        return f"{str(month)[:3]}_{str(year)[2:]}".lower()

    def run_query(self):
        base_query = self.build_base_query()
        base_query_result = self._run_query(base_query)

        dict_query = base_query_result.to_dict(orient="records")
        print(base_query, len(dict_query))
        query_status = {
            "status": None
        }
        for query_result in dict_query:
            metric_key = self.get_metric_key()
            query_status['metric_key'] = metric_key
            if metric_key not in query_result:
                self.message = "The text could not be validated. We do not have enough information to do this."
                self.validity.is_valid = False
                self.validity.invalidity_reason = "INSUFFICIENT_DATA"
            else:
                if query_result.get(metric_key) == self.metric.metric_value:
                    self.validity.is_valid = True
                    self.message = "The text is correct."
                    query_status['status'] = True
                    query_status['result'] = query_result
                    break
                else:
                    self.message = "The text contains an error"
                    self.validity.is_valid = False
                    self.validity.invalidity_reason = "INVALID_METRIC"
                    query_status['result'] = query_result

        if 'result' in query_status:
            country_data = {
                "country": query_status['result']["country"],
                "indicator": query_status['result']["indicator"],
                "source": query_status['result']["source"],
                "link": query_status['result']["link"],
                "currency_code": query_status['result']["currency_code"],
                "unit": query_status['result']["unit"],
                "category": query_status['result']["category"],
                "frequency": query_status['result']["frequency"],
                "note": query_status['result']["note"],
                "tag": query_status['result']["tag"],
                "country_code": query_status['result']["country_code"],
                "indicator_definition": query_status['result']["indicator_definition"],
                "value": query_status['result'].get(query_status['metric_key']),
            }
            return self.serialize_result(country_data)

    def get_metric_key(self):
        metric_key = None
        if self.metric.metric_month:
            if self.metric.metric_year:
                month_year = self.build_month_year_format(self.metric.metric_month, self.metric.metric_year)
                if "Unk" in month_year:
                    self.message = "The text could not be validated. Month missing"
                    self.validity.is_valid = False
                    self.validity.invalidity_reason = "MONTH_MISSING"
                else:
                    metric_key = month_year
        else:
            if self.metric.metric_year:
                if "Unk" in self.metric.metric_year:
                    self.message = "The text could not be validated. Year missing"
                    self.validity.is_valid = False
                    self.validity.invalidity_reason = "YEAR_MISSING"
                else:
                    metric_key = self.metric.metric_year
        return metric_key

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
