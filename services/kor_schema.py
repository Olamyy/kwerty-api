from kor import create_extraction_chain, Object, Text, Number

from config import PROMPT_EXAMPLE


def get_schema(llm, user_text):
    metrics_schema = Object(
        id="country_metrics",
        description="List of metrics measured for a country",
        attributes=[
            Number(
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
                description="The value of the metric",
                examples=[(PROMPT_EXAMPLE, "5.6")],
            ),
        ],
        examples=[
            (
                PROMPT_EXAMPLE,
                {
                    "metric_year": 2003,
                    "metric_name": "Retail Trade Growth",
                    "metric_month": "November",
                    "metric_source": "OECD",
                    "metric_value": "5.6",
                },
            )
        ],
        many=True,
    )

    schema = Object(
        id="country",
        description="Measured metrics about one or more countries",
        attributes=[
            Text(
                id="country",
                description="The country the metric was measured for",
                examples=[(PROMPT_EXAMPLE, "Norway")],
            ),
            metrics_schema,
        ],
        many=True,
    )

    chain = create_extraction_chain(llm, schema, encoder_or_encoder_class="json")
    result = chain.predict_and_parse(text=user_text)

    return result
