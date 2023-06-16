from pydantic import BaseSettings

HOW_DO_I_QUESTIONS = [
    "How do I create a backend plugin?",
    "How do I create a frontend plugin?",
]

BASE_INSTRUCTION = """You need to parse unstructured data into a structured format. The data is in the form of an 
article that contains measured metrics about countries. Your task is to extract the relevant information and output 
it in a JSON format. The JSON should contain an array with country and metric information. The country name should be 
in the "country" field, and the metrics should be in the "metrics" field. The metrics field should be an array of 
JSON objects with fields for the metric measured as 'metric', year, month, value, source, and summary. The "value" 
field should always contain a number. If no data source is provided, the "source" field should be left blank. 
Finally, the "summary" field should be a report generated based on the JSON data. The returned JSON MUST be valid. 
The format of the result should be [{'country': 'COUNTRY', 'metrics': [{'metric': 'METRIC', 'month': 'MONTH', 
'source': 'SOURCE', 'value': VALUE, 'year': YEAR}]}]"""
PROMPT_EXAMPLE = (
    "The Retail Trade Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly. In "
    "November 2003, it was 5.6 . In 1983, it was 3.1 with a low of -1.3 in 2014 and a high of 3.2 in 2019"
)
SUMMARY_INSTRUCTION = "Generate a report on the data below."
FORMAT_JSON_STRING = "Format the JSON string below to make sure it is valid."
MAX_TOKENS = 1000
MODEL_TEMPERATURE = 1
MODEL_TOP_P = 0.95
MODEL_N = 1
ERROR_REASONS = {
    "CountryNotSupported": "The country in the text is not supported",
    "NoMetricsFound": "No metrics found in extraction",
}

STORED_RESPONSES = {
    "The Retail Trade Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly.  In November 2003, it was 5.6 .": {
        "extracted_information": [
            {
                "country": "Norway",
                "country_metrics": [
                    {
                        "metric_year": 2003,
                        "metric_name": "Retail Trade Growth",
                        "metric_month": "November",
                        "metric_source": "OECD",
                        "metric_value": 5.6,
                    }
                ],
            }
        ]
    },
    "The Retail Trade Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly.  It was recorded as 1.4 in September 1997.": {
        "extracted_information": [
            {
                "country": "Norway",
                "country_metrics": [
                    {
                        "metric_year": 1997,
                        "metric_name": "Retail Trade Growth",
                        "metric_month": "September",
                        "metric_source": "OECD",
                        "metric_value": "1.4",
                    }
                ],
            }
        ]
    },
    "The Retail Trade Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly.  It was recorded as 1.4 in September 1997. In 2003, it was 5.6 .": {
        "extracted_information": [
            {
                "country": "Norway",
                "country_metrics": [
                    {
                        "metric_year": 1997,
                        "metric_name": "Retail Trade Growth",
                        "metric_month": "September",
                        "metric_source": "OECD",
                        "metric_value": "1.4",
                    },
                    {
                        "metric_year": 2003,
                        "metric_name": "Retail Trade Growth",
                        "metric_month": "Unknown",
                        "metric_source": "OECD",
                        "metric_value": "5.6",
                    },
                ],
            }
        ]
    },
    "The Broad Money Growth for Norway has been monitored monthly by the OECD since 2010. From 2010 to 2021, the value has fluctuated, with a low of -1.3 in 2014 and a high of 3.2 in 2019. In 2010, the value increased from 0.7 in May to 1 in June, and then decreased to 0 in July and 0.6 in September. In 2011, the value increased from 0 in January to 1.1 in November. In 2012, the value increased from 0.1 in January to 0.7 in December. In 2013, the value increased from 1.3 in January to 0.6 in December. In 2014, the value decreased from 1.4 in January to -1.3 in May. From 2015 to 2021, the Broad Money Growth for Norway": {
        "extracted_information": [
            {
                "country": "Norway",
                "country_metrics": [
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "May",
                        "metric_source": "OECD",
                        "metric_value": 0.7,
                    },
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "June",
                        "metric_source": "OECD",
                        "metric_value": 1,
                    },
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "July",
                        "metric_source": "OECD",
                        "metric_value": 0,
                    },
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "September",
                        "metric_source": "OECD",
                        "metric_value": 0.6,
                    },
                    {
                        "metric_year": 2011,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 0,
                    },
                    {
                        "metric_year": 2011,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "November",
                        "metric_source": "OECD",
                        "metric_value": 1.1,
                    },
                    {
                        "metric_year": 2012,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 0.1,
                    },
                    {
                        "metric_year": 2012,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 0.7,
                    },
                    {
                        "metric_year": 2013,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 1.3,
                    },
                    {
                        "metric_year": 2013,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 0.6,
                    },
                    {
                        "metric_year": 2014,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 1.4,
                    },
                    {
                        "metric_year": 2014,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "May",
                        "metric_source": "OECD",
                        "metric_value": -1.3,
                    },
                    {
                        "metric_year": 2015,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 1.1,
                    },
                    {
                        "metric_year": 2015,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2016,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2016,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2017,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2017,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2018,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2018,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2019,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 2.1,
                    },
                    {
                        "metric_year": 2019,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 3.2,
                    },
                    {
                        "metric_year": 2020,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 3.2,
                    },
                    {
                        "metric_year": 2020,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 3.2,
                    },
                    {
                        "metric_year": 2021,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 3.2,
                    },
                ],
            }
        ]
    },
    "From 2015 to 2021, the Broad Money Growth for Norway has seen a steady rise. In 2015, the value ranged from 0.2 in January to 0.9 in October. In 2016, the value ranged from -0.1 in January to 1.1 in March. In 2017, the value ranged from -0.1 in January to 1.2 in May. In 2018, the value ranged from 0.6 in January to 0.4 in December. In 2019, the value ranged from 0.2 in January to 3.2 in May. In 2020, the value ranged from 0.3 in January to 1.3 in June. In 2021, the value was 1.1 in January.": {
        "extracted_information": [
            {
                "country": "Norway",
                "country_metrics": [
                    {
                        "metric_year": 2015,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": 0.2,
                    },
                    {
                        "metric_year": 2015,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "October",
                        "metric_source": "Unknown",
                        "metric_value": 0.9,
                    },
                    {
                        "metric_year": 2016,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": -0.1,
                    },
                    {
                        "metric_year": 2016,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "March",
                        "metric_source": "Unknown",
                        "metric_value": 1.1,
                    },
                    {
                        "metric_year": 2017,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": -0.1,
                    },
                    {
                        "metric_year": 2017,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "May",
                        "metric_source": "Unknown",
                        "metric_value": 1.2,
                    },
                    {
                        "metric_year": 2018,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": 0.6,
                    },
                    {
                        "metric_year": 2018,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "Unknown",
                        "metric_value": 0.4,
                    },
                    {
                        "metric_year": 2019,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": 0.2,
                    },
                    {
                        "metric_year": 2019,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "May",
                        "metric_source": "Unknown",
                        "metric_value": 3.2,
                    },
                    {
                        "metric_year": 2020,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": 0.3,
                    },
                    {
                        "metric_year": 2020,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "June",
                        "metric_source": "Unknown",
                        "metric_value": 1.3,
                    },
                    {
                        "metric_year": 2021,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "Unknown",
                        "metric_value": 1.1,
                    },
                ],
            }
        ]
    },
    "The Broad Money Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly. The trend from 2010 to 2021 shows that the value has been relatively stable, with a low of -1.3 in 2014 and a high of 3.2 in 2019. In 2010, the value was 0.7 in May, 1 in June, 0 in July, and 0.6 in September. In 2011, the value ranged from 0 in January to 1.1 in November. In 2012, the value ranged from 0.1 in January to 0.7 in December. In 2013, the value ranged from 1.3 in January to 0.6 in December. In 2014, the value ranged from 1.4 in January to -1.3 in May.": {
        "extracted_information": [
            {
                "country": "Norway",
                "country_metrics": [
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "May",
                        "metric_source": "OECD",
                        "metric_value": 0.7,
                    },
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "June",
                        "metric_source": "OECD",
                        "metric_value": 1,
                    },
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "July",
                        "metric_source": "OECD",
                        "metric_value": 0,
                    },
                    {
                        "metric_year": 2010,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "September",
                        "metric_source": "OECD",
                        "metric_value": 0.6,
                    },
                    {
                        "metric_year": 2011,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 0,
                    },
                    {
                        "metric_year": 2011,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "November",
                        "metric_source": "OECD",
                        "metric_value": 1.1,
                    },
                    {
                        "metric_year": 2012,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 0.1,
                    },
                    {
                        "metric_year": 2012,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 0.7,
                    },
                    {
                        "metric_year": 2013,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 1.3,
                    },
                    {
                        "metric_year": 2013,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "December",
                        "metric_source": "OECD",
                        "metric_value": 0.6,
                    },
                    {
                        "metric_year": 2014,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "January",
                        "metric_source": "OECD",
                        "metric_value": 1.4,
                    },
                    {
                        "metric_year": 2014,
                        "metric_name": "Broad Money Growth",
                        "metric_month": "May",
                        "metric_source": "OECD",
                        "metric_value": -1.3,
                    },
                ],
            }
        ]
    },
}


class KwertyAPIConfig(BaseSettings):
    app_name: str = "Kwerty API"
    environment: str
    openai_api_key: str
    openai_temperature: float = 1.0
    openai_n: int = 1
    openai_max_tokens: int = 3200
    openai_top_p: float = 0.95
    openai_model_name: str = "text-davinci-003"
    openai_chat_name: str = "gpt-3.5-turbo"
