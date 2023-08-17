import asyncio
import streamlit as st
from typing import List, Union

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_skills import DataSkill

from utils import get_answer, get_dataframes

ERR_MSG = """Error with query, either I was unable to code the write solution or I couldn't 
understand your query. Apologies, maybe try rewording your question?
"""

# Used at runtime
vars = dict()
kernel: sk.Kernel

if "messages" not in st.session_state:
    st.session_state.messages = []


def clear_history():
    st.session_state.messages = []


def load_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Add new bot message underneath previous content
def add_message(
    msg: Union[str, List[str]], role: str = "assistant", keep_history: bool = False
):
    with st.chat_message(role):
        if isinstance(msg, List):
            for m in msg:
                st.write(m)

            if keep_history:
                st.session_state.messages.append({"role": role, "content": m})
        else:
            st.write(msg)

            if keep_history:
                st.session_state.messages.append({"role": role, "content": msg})


async def files_and_queries():
    files = st.file_uploader(
        "Upload CSV file(s)",
        accept_multiple_files=True,
        type="csv",
        on_change=clear_history,
    )

    if len(files):
        dataframes = get_dataframes(files)
        vars["ds_instance"].add_data(*dataframes)

        add_message("What do you want to know about?")

        load_history()
        if query := st.chat_input():
            add_message(query, "user", True)

            answer = ""
            try:
                answer = await get_answer(query, vars["query_func"])
            except:
                answer = ERR_MSG

            # Known bug, need to fix
            if answer == query:
                answer = ERR_MSG

            add_message(answer, "assistant", True)


def setup(api_key):
    chat_service = OpenAIChatCompletion("gpt-3.5-turbo", api_key)

    kernel = sk.Kernel()
    kernel.add_chat_service("DataBot", chat_service)
    data_skill_instance = DataSkill(service=chat_service)
    skill_functions = kernel.import_skill(data_skill_instance, "data")
    query_func = skill_functions["queryAsync"]

    vars["kernel"] = kernel
    vars["chat_serv"] = chat_service
    vars["ds_instance"] = data_skill_instance
    vars["query_func"] = query_func


async def main():
    st.title("DataBot 🤖")
    st.subheader("An AI-powered data analysis tool.")
    st.caption("Made with :heart: by [sneha-afk](https://github.com/sneha-afk)")

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

    if api_key := api_key_input:
        add_message("Great! Please upload some CSV data for me to analyze!")
        setup(api_key)
        await files_and_queries()


if __name__ == "__main__":
    asyncio.run(main())
