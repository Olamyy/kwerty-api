import dataclasses
from pprint import pprint
from string import punctuation
from typing import Dict, List

import pandas
from fastapi import HTTPException

from config import ERROR_REASONS
from services import STARTUP_OBJECTS
from services.pandas_query import PandasQuery, CountryMetric, Validity


@dataclasses.dataclass
class ExtractionError:
    error: bool
    error_reason: str


@dataclasses.dataclass
class Position:
    offset: int
    length: int


@dataclasses.dataclass
class Match:
    position: Position
    message: str
    openai_extract: CountryMetric = None
    kwerty_validation: Dict = None
    validity: Validity = None


@dataclasses.dataclass
class MetricMatch:
    matches: List[Match] = None

    def __post_init__(self):
        if not self.matches:
            self.matches = []


@dataclasses.dataclass
class CountryResultManager:
    metric_match: MetricMatch = None
    error: ExtractionError = None

    def __post_init__(self):
        if not self.error:
            self.metric_match = MetricMatch()


class MetricsManager:
    def __init__(self, user_text: str, country_data: List[Dict]):
        self.user_text = user_text
        self.country_data = country_data
        self.validation_data: pandas.DataFrame = STARTUP_OBJECTS["validation_data"]
        self.columns = self.get_columns()
        self.result = CountryResultManager()

    def process_metrics(self):
        country_names = self.get_supported_countries()
        for country_information in self.country_data:
            country_name = country_information.get("country", self.guess_country_name(country_names))
            if not country_name:
                if not country_name:
                    raise HTTPException(
                        status_code=502,
                        detail={
                            "message": "Could not extract country name.",
                            "data": self.country_data,
                        },
                    )
            if country_name not in country_names:
                self.result.error = ExtractionError(
                    error=True, error_reason=ERROR_REASONS["CountryNotSupported"]
                )
            else:
                metrics = country_information["country_metrics"]
                if not metrics:
                    self.result.error = ExtractionError(
                        error=True, error_reason=ERROR_REASONS["NoMetricsFound"]
                    )
                else:
                    metrics = [CountryMetric(**metric) for metric in metrics]
                    metric_values = [metric.metric_value for metric in metrics]
                    try:
                        for metric, offset in zip(
                                metrics,
                                self.get_word_positions(self.user_text, metric_values),
                                # strict=True
                        ):
                            pandas_query_handler = PandasQuery(
                                country_name=country_name,
                                metric=metric,
                                validation_data=self.validation_data,
                                columns=self.columns,
                            )

                            validated_data = pandas_query_handler.run_query()
                            print(validated_data)
                            match = Match(
                                position=Position(
                                    length=len(metric.metric_value), offset=offset
                                ),
                                openai_extract=metric,
                                kwerty_validation=validated_data,
                                validity=pandas_query_handler.validity,
                                message=pandas_query_handler.message,
                            )
                            self.result.metric_match.matches.append(match)
                    except ValueError:
                        raise HTTPException(
                            status_code=502,
                            detail={
                                "message": "Metric match. The metric count in the sentence does not match the count "
                                           "returned by OpenAI",
                                "error_type": "METRIC_MISMATCH",
                                "data": self.country_data,
                            },
                        )

        return self.result

    def get_supported_countries(self):
        return set(self.validation_data["country"].to_list())

    def get_columns(self):
        return set(self.validation_data.columns.to_list())

    @staticmethod
    def get_word_positions(text, metric_values):
        positions = []
        for index, word in enumerate(text.split()):
            if word.rstrip(punctuation) in metric_values:
                positions.append(index)

        return positions

    def guess_country_name(self, country_names):
        valid_countries = set(
            country for country in country_names if country in [word.rstrip(punctuation) for word in self.user_text.split(" ")]
        )
        if valid_countries:
            return list(valid_countries)[0]

