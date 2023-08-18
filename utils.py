import streamlit as st
import pandas as pd
import requests


def authenticate_key(api_key: str) -> bool:
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


def clear_message_view():
    """Still available in the string for downloading"""
    st.session_state.messages = []


def load_messages():
    for message in st.session_state.messages:
        add_message(message["content"], message["role"])


@st.cache_data
def load_into_dataframe(data) -> pd.DataFrame:
    """Wrapping with ST's caching function"""
    print("caching new file:", data.name)
    return pd.read_csv(data)
