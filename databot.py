import asyncio
import streamlit as st

from datetime import datetime
from utils import (
    authenticate_key,
    files_changed,
    load_into_dataframe,
    add_message,
    load_messages,
    kernel_setup,
)

ERR_MSG = "Error with query: I might have misinterpreted you, try rewording your query. Apologies!"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history_string" not in st.session_state:
    st.session_state.chat_history_string = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "kernel_setup" not in st.session_state:
    st.session_state.kernel_setup = False
if "reload_files" not in st.session_state:
    st.session_state.reload_files = False

# ========= ENTER =========
st.title("DataBot 🤖")
st.subheader("An AI-powered natural language data analysis tool.")
st.caption("Made with :heart: by [sneha-afk](https://github.com/sneha-afk)")

add_message(
    "Hello there, my name is DataBot :wave:. I make data analysis as easy as can be!"
)

with st.sidebar:
    st.title("SideBar-Bot?")
    st.subheader("Don't steal that.")
    st.caption("[View DataBot's source code](https://github.com/sneha-afk/databot)")
    st.divider()
    st.subheader("OpenAI API Key")

    api_key_input = st.text_input(
        "Press *Authenticate* after entering:",
        type="password",
        help="Visit OpenAI to obtain an API key!",
        placeholder="sk-...",
    )
    api_submitted = st.button("Authenticate")

# =========================


async def query():
    load_messages()
    if query := st.chat_input():
        add_message(query, "user", True)

        answer = ""
        try:
            from_func = await st.session_state["query_func"].invoke_async(query)
            answer = from_func.result.strip("`")
        except:
            answer = ERR_MSG

        # Known bug, need to fix
        if answer == query:
            answer = ERR_MSG

        add_message(answer, "assistant", True)

    if len(st.session_state.messages):
        st.download_button(
            "Download chat history",
            data=st.session_state.chat_history_string,
            file_name=f"databot_chat_history_{datetime.now().strftime('%Y-%m-%d-%H:%M')}.txt",
            help="Get a text file containing all of your chat history",
        )


async def files():
    files = st.file_uploader(
        "Upload CSV file(s) for me to analyze!",
        accept_multiple_files=True,
        type="csv",
        on_change=files_changed,
    )

    if st.session_state.reload_files:
        # As of 8/16/23: removing specific dataframes is not supported
        # Inefficient to keep clearing, will look to make this better
        st.session_state["ds_instance"].clear_data()
        for file in files:
            st.session_state["ds_instance"].add_data(load_into_dataframe(file))

        st.session_state.reload_files = False

    if len(files):
        add_message("What do you want to know about?")
        await query()


async def main():
    # If user submitted on previous run, reauthenticate and setup kernel
    if api_submitted:
        st.session_state.authenticated = authenticate_key(api_key_input)
        st.session_state.kernel_setup = False

    if st.session_state.authenticated:
        # Setup once per API key entry
        if not st.session_state.kernel_setup:
            st.session_state.kernel_setup = kernel_setup(api_key_input)

        with st.sidebar:
            st.success("Authentication complete!")
    elif api_submitted:  # User pressed submit but authentication failed
        with st.sidebar:
            st.error(
                ":warning: Error with authentication, please confirm your key is valid."
            )

    if st.session_state.kernel_setup:
        await files()


if __name__ == "__main__":
    asyncio.run(main())
