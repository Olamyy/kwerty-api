from kor import create_extraction_chain, Object, Text, Number, from_pydantic
from pydantic import BaseModel, Field
from typing import List, Optional

from config import PROMPT_EXAMPLE


class CountryMetrics(BaseModel):
    metric_year: Optional[str] = Field(
        description="The year the metric was measured",
        examples=[(PROMPT_EXAMPLE, "2003")],
    )
    metric_value: Optional[str] = Field(
        description="The value of the metric",
        examples=[(PROMPT_EXAMPLE, "5.6")],

    )
    metric_source: Optional[str] = Field(
        description="The source of the metric",
        examples=[(PROMPT_EXAMPLE, "OECD")],

    )
    metric_month: Optional[str] = Field(
        description="The month the metric was measured in",
        examples=[(PROMPT_EXAMPLE, "November")],

    )
    metric_name: str = Field(
        description="The name of the metric that was measured",
        examples=[(PROMPT_EXAMPLE, "Retail Trade Growth for Norway")],
    )


class ExtractedInformation(BaseModel):
    country: Optional[str] = Field(
        description="The country the metric was measured for.",
        examples=[(PROMPT_EXAMPLE, "Norway")],
    )
    country_metrics: List[CountryMetrics] = Field(
        description="The action that should be taken; one of `play`, `stop`, `next`, `previous`",
        examples=[
            ("Please stop the music", "stop"),
            ("play something", "play"),
            ("play a song", "play"),
            ("next song", "next"),
        ],
    )


def get_schema(llm, user_text, include_example=None):
    examples = [
        (
            PROMPT_EXAMPLE,
            {
                "metric_year": 2003,
                "metric_name": "Retail Trade Growth",
                "metric_month": "November",
                "metric_source": "OECD",
                "metric_value": "5.6",
            },
        ),
        (
            PROMPT_EXAMPLE,
            {
                "metric_year": 1983,
                "metric_name": "Retail Trade Growth",
                "metric_source": "OECD",
                "metric_value": "3.1"
            }
        )
    ]
    metrics_schema = Object(
        id="country_metrics",
        description="List of metrics measured for a country",
        attributes=[
            Text(
                id="metric_year",
                description="The year the metric was measured",
                examples=[(PROMPT_EXAMPLE, "2003")],
            ),
            Text(
                id="metric_name",
                description="The name of the metric that was measured",
                examples=[(PROMPT_EXAMPLE, "Retail Trade Growth for Norway")],
            ),
            Text(
                id="metric_month",
                description="The month the metric was measured in",
                examples=[(PROMPT_EXAMPLE, "November")],
            ),
            Text(
                id="metric_source",
                description="The source of the metric",
                examples=[(PROMPT_EXAMPLE, "OECD")],
            ),
            Number(
                id="metric_value",
                description="The value of the metric. It should either be an integer or decimal number",
                examples=[(PROMPT_EXAMPLE, "5.6")],
            ),
        ],
        examples=examples,
        many=True,
    )

    if include_example:
        examples.append(include_example)

    schema = Object(
        id="extracted_information",
        description="Measured metrics about one or more countries",
        attributes=[
            Text(
                id="country",
                description="The country the metric was measured for",
                examples=[(PROMPT_EXAMPLE, "Norway")],
            ),
            metrics_schema,
        ],
        examples=examples,
        many=True,
    )

    chain = create_extraction_chain(llm, schema, encoder_or_encoder_class="json")
    result = chain.predict_and_parse(text=user_text)
    return result
