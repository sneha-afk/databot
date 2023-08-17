import asyncio
import streamlit as st
import pandas as pd
import numpy as np
import semantic_kernel as sk
from utils import *
from typing import List, Union


variables = dict()


# Add new bot message underneath previous content
def add_message(
    msg: Union[str, List[str]],
    role: str = "assistant",
):
    with st.chat_message(role):
        if isinstance(msg, List):
            for m in msg:
                st.write(m)
        else:
            st.write(msg)


def starting():
    st.title("DataBot 🤖")
    st.subheader("An AI-powered data analysis tool.")

    add_message(
        [
            "Hello there, my name is DataBot. 👋",
            "Please enter your OpenAI API key to begin!",
        ]
    )

    api_key_input = st.text_input(
        "OpenAI API key",
        type="password",
        help="Visit OpenAI to obtain an API key!",
        placeholder="abc-...",
    )
    return api_key_input


async def main():
    if api_key := starting():
        add_message(
            "Great! Now upload CSV data for me to analyze along with your query."
        )
        files = st.file_uploader(
            "Upload CSV file(s)", accept_multiple_files=True, type="csv"
        )

        if len(files):
            dataframes = get_dataframes(files)
            query_func = setup(api_key, dataframes)

            add_message("And what would you like to know about this data?")

            # query = st.chat_input()
            # if query:
            #     add_message(query, "user")
            # answer = await query_func.invoke_async(query)
            # add_message(answer)

            query = st.text_area(
                "Query for data", placeholder="What is the average value of..."
            )

            if st.button("Submit"):
                answer = await get_answer(query, query_func)
                add_message(answer)


if __name__ == "__main__":
    asyncio.run(main())
