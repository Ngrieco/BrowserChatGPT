import streamlit as st
import validators

from src.browser_llm import BrowserLLM
from src.web_data import WebData
from src.web_scraper import WebScraper


@st.cache_resource
def get_llm(url):
    web_scraper = WebScraper(max_links=1)

    _, data = web_scraper.scrape_data_bfs_priority(url)

    # store scraped data locally for debugging
    file_path = "data.txt"
    with open(file_path, "w") as file:
        file.write(data)

    web_data = WebData([data])

    llm = BrowserLLM(web_data)

    return llm


if "global_data" not in st.session_state:
    st.session_state.global_data = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("BrowserChatGPT")

form = st.form(key="my_form")
url = form.text_input(label="Enter website you'd like to chat with")
submit = form.form_submit_button(label="Submit")

if submit:
    valid_url = validators.url(url)
    if valid_url:
        try:
            print("Trying to load QA model.")
            llm = get_llm(url)
            st.session_state.global_data["llm"] = llm
            st.header("Now chatting with {}".format(url))
            st.session_state.messages = []
        except Exception as e:
            st.header("Unable to load current URL")
            st.header("{}".format(e))
    else:
        st.header("Invalid URL: {}".format(url))


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I assist you?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        if "llm" in st.session_state.global_data:
            llm = st.session_state.global_data["llm"]
            full_response = llm.query(prompt)
        else:
            full_response = "You must enter a valid URL to begin chatting."

        message_placeholder.markdown(full_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
