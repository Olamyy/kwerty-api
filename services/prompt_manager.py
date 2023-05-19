import json

import openai
from gptcache import Cache, cache
from gptcache.manager import manager_factory
from gptcache.processor.pre import get_prompt
from langchain.chat_models import ChatOpenAI
from gptcache.adapter.langchain_models import LangChainChat

from config import (
    BASE_INSTRUCTION,
    MODEL_TEMPERATURE,
    MODEL_TOP_P,
    MODEL_N,
    MAX_TOKENS,
    SUMMARY_INSTRUCTION,
    FORMAT_JSON_STRING,
)
from services.kor_schema import get_schema


class KorPromptManager:
    def __init__(self, user_text: str):
        self.user_text = user_text

    @staticmethod
    def get_msg(data, **_):
        return data.get("messages")[-1].content

    def run(self):
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=MODEL_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=MODEL_TOP_P,
            n=MODEL_N,
            frequency_penalty=0,
            presence_penalty=0,
        )
        cache.init(
            pre_embedding_func=self.get_msg,
        )
        extracted_schema = get_schema(LangChainChat(chat=llm), self.user_text)

        return extracted_schema

    @staticmethod
    def init_gptcache(cache_obj: Cache, llm: str):
        cache_obj.init(
            pre_embedding_func=get_prompt,
            data_manager=manager_factory(manager="map", data_dir=f"map_cache_{llm}"),
        )


class PromptManager:
    def __init__(self, user_text: str):
        self.user_text = user_text
        self.cleaned_user_text = self.clean_user_text()

    def clean_user_text(self):
        return self.user_text

    def build_prompt(self):
        return f"""{BASE_INSTRUCTION}\n'{self.cleaned_user_text}'"""

    @staticmethod
    def build_summary_prompt(dict_data):
        return f"{SUMMARY_INSTRUCTION} {dict_data}"

    @staticmethod
    def build_json_formatting_prompt(json_string):
        return f"{FORMAT_JSON_STRING}\n {json_string}"

    @classmethod
    def clean_prompt_response(cls, prompt_result: str, return_json=True):
        prompt_result = prompt_result.replace("\n", "").replace("'", '"')
        if return_json:
            try:
                to_json = json.loads(prompt_result)
                return to_json

            except json.JSONDecodeError as error:
                print(f"Found error: {error}\n Instance : {type(prompt_result)}")
                return cls.validate_json_prompt(
                    cls.build_json_formatting_prompt(prompt_result)
                )

        return prompt_result

    def run_prompt(self):
        self.setup_openai()
        prompt = self.build_prompt()
        prompt_response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=MODEL_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=MODEL_TOP_P,
            n=MODEL_N,
            logprobs=5,
        )
        return self.clean_prompt_response(prompt_response.choices[0]["text"])

    @classmethod
    def generate_summary(cls, dict_data):
        cls.setup_openai()
        prompt = cls.build_summary_prompt(dict_data)
        prompt_response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=MODEL_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=MODEL_TOP_P,
            n=MODEL_N,
            logprobs=5,
        )
        return cls.clean_prompt_response(
            prompt_response.choices[:1][0]["text"], return_json=False
        )

    @classmethod
    def validate_json_prompt(cls, json_string):
        cls.setup_openai()
        prompt = cls.build_json_formatting_prompt(json_string)
        prompt_response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=MODEL_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=MODEL_TOP_P,
            n=MODEL_N,
            logprobs=5,
        )
        return cls.clean_prompt_response(
            prompt_response.choices[:1][0]["text"], return_json=True
        )

    @staticmethod
    def setup_openai():
        openai.api_key = "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"
