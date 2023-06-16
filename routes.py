from pprint import pprint

import nltk
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tinydb import Query
from tinydb.table import Table

from config import STORED_RESPONSES
from services import STARTUP_OBJECTS
from services.metrics_manager import MetricsManager
from services.prompt_manager import KorPromptManager

router = APIRouter()


class UserText(BaseModel):
    text: str


def get_stored(user_text: str):
    response = STORED_RESPONSES.get(user_text)
    if response:
        return response.get('extracted_information')
    return response


def split_text_into_sentences(text_):
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    ignored_tokens = nltk.word_tokenize(". - +")
    sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentence_tokenizer._params.abbrev_types.update(ignored_tokens)

    # Split the text into sentences
    sentences = sentence_tokenizer.tokenize(text_)

    return sentences


def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def check_metrics(db, user_text: str, get_metrics=False):
    query = Query()
    query_result = db.search(query.user_text == user_text)
    if query_result:
        return query_result[0].get('processed_metrics') if get_metrics else query_result[0].get('extracted_information')


def extract_information(user_text, previous=None):
    prompt_manager = KorPromptManager(user_text=user_text)
    prompt_result = prompt_manager.run(previous=previous)
    data = prompt_result["data"]
    pprint(
        prompt_result
    )
    if "extracted_information" not in data:
        pprint(data)
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Something went wrong while contacting OpenAI",
                "data": data,
            },
        )
    return data['extracted_information']


@router.post("/evaluate/")
async def evaluate_text(user_text: UserText):
    db: Table = STARTUP_OBJECTS['db']
    user_text = user_text.text
    sentence_count = split_text_into_sentences(user_text)
    extracted_information = []
    chunks = list(chunkify(sentence_count, 3))[0]
    sliced_chunk = chunks[:3]
    chunk_combined = " ".join(sliced_chunk)
    maybe_metrics = check_metrics(db, user_text)
    if maybe_metrics:
        extracted_information.extend(maybe_metrics)
    else:
        chunk_information = extract_information(chunk_combined)
        extracted_information.extend(chunk_information)
        db.insert(
            {
                "user_text": user_text,
                "extracted_information": extracted_information
            }
        )
    # for chunk in chunks:
    #     chunk_combined = " ".join(chunk)
    #     maybe_metrics = check_metrics(db, chunk_combined)
    #     if maybe_metrics:
    #         extracted_information.extend(maybe_metrics)
    #     else:
    #         print(chunk_combined)
    #         chunk_information = extract_information(chunk_combined, previous=previous)
    #         previous = {
    #             "text": user_text,
    #             "metrics": chunk_information
    #         }
    #         pprint(chunk_information)
    #         extracted_information.extend(chunk_information)
    #         db.insert(
    #             {
    #                 "user_text": user_text,
    #                 "extracted_information": extracted_information
    #             }
    #         )
    metrics = MetricsManager(user_text=user_text, country_data=extracted_information)
    processed_metrics = metrics.process_metrics()
    # pprint(
    #     processed_metrics
    # )
    return processed_metrics
