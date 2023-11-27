import asyncio
import threading

import streamlit as st
import validators
from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore

print("RUNNING STREAMLIT FILE")


def save_pages_to_txt(pages):
    # store scraped data locally for debugging
    file_path = "data.txt"
    with open(file_path, "w") as file:
        for page in pages:
            file.write(page["url"])
            file.write("\n")
            file.write(page["text"])


num_threads = 3
max_links = 6
database_name = "test_web_llm"
vs_lock = threading.Lock()

"""
def scrape(url):
    with ThreadPoolExecutor() as executor:
        print(f"Thread {threading.current_thread()} running scrape")
        scraper = st.session_state.global_data["scraper"]
        result = asyncio.run(executor.submit(scraper.scrape(url)))
        st.write(result)
"""


async def scrape(url):
    scraper = st.session_state.global_data["scraper"]
    await scraper.scrape(url)


def async_scrape(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(scrape(url))
    loop.close()


def start_async_scrape(url):
    print("Creating scrape thread")
    _thread = threading.Thread(target=async_scrape, args=(url,))
    _thread.start()


@st.cache_resource
def initialize():
    print("Initializing all resources")
    pages = [{"url": "NA", "text": "Empty"}]
    vector_store = WebVectorStore(pages, vs_lock)
    cache = WebCache(database_name, num_threads)
    scraper = WebScraperConcurrent(
        cache, vector_store, vs_lock, max_links=max_links, threads=num_threads
    )
    llm = WebLLM(vector_store)

    st.session_state.global_data["vector_store"] = vector_store
    st.session_state.global_data["cache"] = cache
    st.session_state.global_data["scraper"] = scraper
    st.session_state.global_data["llm"] = llm

    return llm


if "global_data" not in st.session_state:
    print("Creating session_state.global_data")
    st.session_state.global_data = {}

if "messages" not in st.session_state:
    print("Creating session_state.messages")
    st.session_state.messages = []

st.title("BrowserChatGPT")

form = st.form(key="my_form")
url = form.text_input(label="Enter website you'd like to chat with")
submit = form.form_submit_button(label="Submit")

initialize()

if submit:
    print("Submit - checking url")
    valid_url = validators.url(url)
    if valid_url:
        try:
            start_async_scrape(url)
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
    st.session_state.messages.append({"role": "assistant", "content": full_response})
