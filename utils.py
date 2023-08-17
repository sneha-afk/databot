import semantic_kernel as sk
from typing import Any, List
import pandas as pd


def get_dataframes(data: List[Any]):
    dfs = list()
    for d in data:
        dfs.append(pd.read_csv(d))
    return dfs


async def get_answer(query: str, func: sk.SKFunctionBase) -> str:
    from_func = await func.invoke_async(query)
    return from_func.result.strip("`")
