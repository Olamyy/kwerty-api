MODEL_NAME = "text-davinci-003"
BASE_INSTRUCTION = """You need to parse unstructured data into a structured format. The data is in the form of an 
article that contains measured metrics about countries. Your task is to extract the relevant information and output 
it in a JSON format. The JSON should contain an array with country and metric information. The country name should be 
in the "country" field, and the metrics should be in the "metrics" field. The metrics field should be an array of 
JSON objects with fields for the metric measured as 'metric', year, month, value, source, and summary. The "value" 
field should always contain a number. If no data source is provided, the "source" field should be left blank. 
Finally, the "summary" field should be a report generated based on the JSON data. The returned JSON MUST be valid. 
The format of the result should be [{'country': 'COUNTRY', 'metrics': [{'metric': 'METRIC', 'month': 'MONTH', 
'source': 'SOURCE', 'value': VALUE, 'year': YEAR}]}]"""
SUMMARY_INSTRUCTION = "Generate a report on the data below."
FORMAT_JSON_STRING = "Format the JSON string below to make sure it is valid."
MAX_TOKENS = 3000
MODEL_TEMPERATURE = 1
MODEL_TOP_P = 0.95
MODEL_N = 1
