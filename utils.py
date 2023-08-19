import streamlit as st
import pandas as pd
import requests

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_skills import DataSkill


def authenticate_key(api_key: str) -> bool:
    if not api_key.startswith("sk-"):
        return False

    auth_request = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    model_list_url = "https://api.openai.com/v1/models"
    response = requests.get(model_list_url, headers=auth_request)

    # Successful API call?
    return response.status_code == 200


# Add new bot message underneath previous content
def add_message(msg: str, role: str = "assistant", keep_history: bool = False):
    with st.chat_message(role):
        st.markdown(msg)

        if keep_history:
            st.session_state.messages.append({"role": role, "content": msg})
            st.session_state.chat_history_string += (
                f"{'User' if role == 'user' else 'DataBot'}:> {msg}\n\n"
            )


def files_changed():
    """Preivous history is not erased and can be downloaded"""
    st.session_state.messages = []
    st.session_state.reload_files = True


def load_messages():
    for message in st.session_state.messages:
        add_message(message["content"], message["role"])


@st.cache_data
def load_into_dataframe(data) -> pd.DataFrame:
    """Wrapping with ST's caching decorator"""
    return pd.read_csv(data)


def kernel_setup(api_key: str) -> bool:
    try:
        chat_service = OpenAIChatCompletion("gpt-3.5-turbo", api_key)

        kernel = sk.Kernel()
        kernel.add_chat_service("DataBot", chat_service)
        data_skill_instance = DataSkill(service=chat_service)
        skill_functions = kernel.import_skill(data_skill_instance, "data")
        query_func = skill_functions["queryAsync"]

        st.session_state["kernel"] = kernel
        st.session_state["ds_instance"] = data_skill_instance
        st.session_state["query_func"] = query_func

        return True
    except:
        # Unsuccessful setup
        return False

    st.session_state.kernel_setup = True
