import streamlit as st
import pandas as pd
import numpy as np
import semantic_kernel as sk
from utils import *
from typing import List, Union


kernel: sk.Kernel = None


# Add new bot message underneath previous content
def add_bot_msg(msg: Union[str, List[str]]):
    with st.chat_message("assistant"):
        if isinstance(msg, List):
            for m in msg:
                st.write(m)
        else:
            st.write(msg)


def starting():
    st.title("DataBot 🤖")
    st.subheader("An AI-powered data analysis tool.")

    add_bot_msg(
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


api_key_obtained = False
if api_key := starting():
    kernel = setup(api_key)

    add_bot_msg("Great! Now upload CSV data for me to analyze along with your query.")
    files = st.file_uploader(
        "Upload CSV file(s)", accept_multiple_files=True, type="csv"
    )

    if len(files):
        dataframes = get_dataframes(files)

        add_bot_msg("And what would you like to know about this data?")
