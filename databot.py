import asyncio
import streamlit as st
import pandas as pd

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_skills import DataSkill

from utils import (
    authenticate_key,
    clear_message_view,
    load_into_dataframe,
    add_message,
    load_messages,
)

ERR_MSG = "Error with query: I might have misinterpreted you, try rewording your query. Apologies!"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history_string" not in st.session_state:
    st.session_state.chat_history_string = ""
if "prev_num_files" not in st.session_state:
    st.session_state.prev_num_files = 0


async def query():
    load_messages()
    if query := st.chat_input():
        add_message(query, "user", True)

        answer = ""
        try:
            from_func = await st.session_state["query_func"].invoke_async(query)
            answer = from_func.result.strip("`")
        except Exception as e:
            print(type(e))
            answer = ERR_MSG

        # Known bug, need to fix
        if answer == query:
            answer = ERR_MSG

        add_message(answer, "assistant", True)

    if len(st.session_state.messages):
        st.download_button(
            "Download chat history",
            data=st.session_state.chat_history_string,
            file_name="databot_chat_history.txt",
            help="Get a text file containing all of your chat history",
        )


async def files_and_queries():
    files = st.file_uploader(
        "Upload CSV file(s)",
        accept_multiple_files=True,
        type="csv",
        on_change=clear_message_view,
    )

    if len(files):
        # As of 8/16/23: removing specific dataframes is not supported
        if (
            st.session_state["prev_num_files"] == 0
            or len(files) != st.session_state["prev_num_files"]
        ):
            st.session_state["ds_instance"].clear_data()

            # Add new dataframes, or load from cache
            for file in files:
                st.session_state["ds_instance"].add_data(load_into_dataframe(file))

        add_message("What do you want to know about?")

        await query()
    st.session_state["prev_num_files"] = len(files)


def setup(api_key):
    chat_service = OpenAIChatCompletion("gpt-3.5-turbo", api_key)

    kernel = sk.Kernel()
    kernel.add_chat_service("DataBot", chat_service)
    data_skill_instance = DataSkill(service=chat_service)
    skill_functions = kernel.import_skill(data_skill_instance, "data")
    query_func = skill_functions["queryAsync"]

    st.session_state["kernel"] = kernel
    st.session_state["ds_instance"] = data_skill_instance
    st.session_state["query_func"] = query_func


async def main():
    st.title("DataBot 🤖")
    st.subheader("An AI-powered natural language data analysis tool.")

    st.caption(
        "Made with :heart: by [sneha-afk](https://github.com/sneha-afk) -- [source code](https://github.com/sneha-afk/databot)"
    )
    add_message(
        "Hello there, my name is DataBot 👋. I make data analysis as easy as can be!\n\nEnter a valid OpenAI API key to begin!"
    )

    api_key_input = st.text_input(
        "OpenAI API key",
        type="password",
        help="Visit OpenAI to obtain an API key!",
        placeholder="sk-...",
    )

    if api_key := api_key_input:
        if authenticate_key(api_key):
            add_message("Great! Now upload CSV data for me to analyze.")
            setup(api_key)
            await files_and_queries()
        else:
            st.error(
                ":warning: Error with validating OpenAI API key, please confirm your key."
            )


if __name__ == "__main__":
    asyncio.run(main())
