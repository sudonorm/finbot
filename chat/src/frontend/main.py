import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8282/api/v1/chat")
# headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}
SLSH = "/"

with st.sidebar:
    st.header("About")
    st.markdown(
        """
        Welcome to FinBot, your friendly financial assistant. You can ask me questions
        about companies (including specific metrics), about recent news about companies or individuals
        and if you feel up to it, you can ask me for the summary of earnings or conference calls of companies
        """
    )

st.title("FinBot")
st.info(
    "Welcome to FinBot. I am your friendly financial assistant, how can I help you today?"
)

from contextlib import contextmanager
from io import StringIO
from threading import current_thread
import streamlit as st
import sys


@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):

            buffer.write(b)
            output_func(buffer.getvalue())

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def st_stderr(dst):
    with st_redirect(sys.stderr, dst):
        yield


if "messages" not in st.session_state:
    st.session_state.messages = []

if "content" not in st.session_state:
    st.session_state.content = {}

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])

if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "output": prompt})

    if len(st.session_state.content) > 0:
        response_bdy = {"session_uuid": st.session_state.content.get("session_uuid")}
    else:
        response_bdy = {}

    with st.spinner("Searching for an answer..."):
        response = requests.post(
            f"{CHATBOT_URL}",
            # headers=headers, ## headers should be enabled if API endpoint Auth is enabled
            json={"question": prompt, "response_bdy": response_bdy, "language": "en"},
        )

        if response.status_code == 200:

            output_text = response.json()["content"]["response"]
            st.session_state.content.update(response.json()["content"])

        else:
            output_text = """An error occurred while processing your message.
            Please try again or rephrase your message."""
            explanation = output_text

    st.chat_message("assistant").markdown(str(output_text))

    st.session_state.messages.append(
        {
            "role": "assistant",
            "output": output_text,
        }
    )

    # print(st.session_state)
