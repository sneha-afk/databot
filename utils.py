import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai import ChatCompletionClientBase
from semantic_kernel.core_skills import DataSkill
from typing import Any, List, Union
import pandas as pd
import streamlit as st


def setup(api_key: str, user_data) -> Kernel:
    openai_chat_completion = OpenAIChatCompletion("gpt-3.5-turbo", api_key)

    kernel = Kernel()
    kernel.add_chat_service("DataBot", openai_chat_completion)

    data_skill = kernel.import_skill(
        DataSkill(data=user_data, service=openai_chat_completion),
        skill_name="data",
    )
    query_async = data_skill["queryAsync"]

    return query_async


def get_dataframes(data: List[Any]):
    dfs = list()
    for d in data:
        dfs.append(pd.read_csv(d))
    return dfs


async def get_answer(query: str, func: sk.SKFunctionBase) -> str:
    from_func = await func.invoke_async(query)
    return from_func.result.strip("`")
