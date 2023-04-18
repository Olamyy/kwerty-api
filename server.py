from pprint import pprint

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from services.metrics_manager import MetricsManager
from services.prompt_manager import PromptManager


def get_user_input(text):
    prompt_manager = PromptManager(user_text=text)
    prompt_result = prompt_manager.run_prompt()
    pprint(
        {
            "prompt_result": prompt_result
        }
    )
    metrics = MetricsManager(prompt_result)
    processed_metrics = metrics.process_metrics()

    return processed_metrics


examples = {
    "The Retail Trade Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly.  "
    "It was recorded as 1.4 in September 1997.": 1,
    "The Retail Trade Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly.  "
    "It was recorded as 1.4 in September 1997. In 2003, it was 5.6 .": 2,
    "The Broad Money Growth for Norway has been monitored monthly by the OECD since 2010. From 2010 to 2021, "
    "the value has fluctuated, with a low of -1.3 in 2014 and a high of 3.2 in 2019. In 2010, the value increased "
    "from 0.7 in May to 1 in June, and then decreased to 0 in July and 0.6 in September. In 2011, the value "
    "increased from 0 in January to 1.1 in November. In 2012, the value increased from 0.1 in January to 0.7 in "
    "December. In 2013, the value increased from 1.3 in January to 0.6 in December. In 2014, the value decreased "
    "from 1.4 in January to -1.3 in May. From 2015 to 2021, the Broad Money Growth for Norway": 3,
    "From 2015 to 2021, the Broad Money Growth for Norway has seen a steady rise. In 2015, the value ranged from 0.2 "
    "in January to 0.9 in October. In 2016, the value ranged from -0.1 in January to 1.1 in March. In 2017, "
    "the value ranged from -0.1 in January to 1.2 in May. In 2018, the value ranged from 0.6 in January to 0.4 in "
    "December. In 2019, the value ranged from 0.2 in January to 3.2 in May. In 2020, the value ranged from 0.3 in "
    "January to 1.3 in June. In 2021, the value was 1.1 in January.": 4,
    "The Broad Money Growth for Norway, as reported by the OECD, is measured in percentages and recorded monthly. "
    "The trend from 2010 to 2021 shows that the value has been relatively stable, with a low of -1.3 in 2014 and a "
    "high of 3.2 in 2019. In 2010, the value was 0.7 in May, 1 in June, 0 in July, and 0.6 in September. In 2011, "
    "the value ranged from 0 in January to 1.1 in November. In 2012, the value ranged from 0.1 in January to 0.7 in "
    "December. In 2013, the value ranged from 1.3 in January to 0.6 in December. In 2014, the value ranged from 1.4 "
    "in January to -1.3 in May.": 5
}

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserText(BaseModel):
    text: str


@app.post("/evaluate/")
async def create_item(user_text: UserText):
    output = get_user_input(user_text.text)
    return {
        "metrics": output,
    }


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
