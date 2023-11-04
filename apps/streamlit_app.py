import streamlit as st
import validators

from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraper
from browserchatgpt.web_vectorstore import WebVectorStore


def save_pages_to_txt(pages):
    # store scraped data locally for debugging
    file_path = "data.txt"
    with open(file_path, "w") as file:
        for page in pages:
            file.write(page["url"])
            file.write("\n")
            file.write(page["text"])


@st.cache_resource
def get_llm(url):
    web_scraper = WebScraper(max_links=3)

    pages = web_scraper.scrape_data_bfs_priority(url)

    save_pages_to_txt(pages)

    web_data = WebVectorStore(pages)

    llm = WebLLM(web_data)

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
            st.caption("Now chatting with {}".format(url))
            st.session_state.messages = []
        except Exception as e:
            st.caption("Unable to load current URL")
            st.caption("{}".format(e))
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
            response = llm.query(prompt)

            full_response = response
            # answer, sources = response["answer"], response["sources"]
            # full_response = answer + "\n" + sources
        else:
            full_response = "You must enter a valid URL to begin chatting."

        message_placeholder.markdown(full_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
