import copy
import threading

import validators

from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore


class BrowserChatGPT:
    def __init__(self, use_robot_txt=True):
        num_threads = 3
        max_links = 100
        database_name = "browserchatgpt"
        vs_lock = threading.Lock()
        self.vector_store = WebVectorStore(vs_lock)
        self.cache = WebCache(database_name, num_threads)
        self.llm = WebLLM(self.vector_store)
        self.scraper = WebScraperConcurrent(
            self.cache,
            self.vector_store,
            vs_lock,
            max_links=max_links,
            num_threads=num_threads,
        )
        self.scraper_thread = None
        self.llm_thread = None
        self.current_url = None
        self.use_robot_txt = use_robot_txt

    def submit_url(self, requested_url):
        self.scraper_thread = threading.Thread(
            target=self.query_scraper,
            args=(
                requested_url,
                self.use_robot_txt,
            ),
        )
        self.scraper_thread.start()

    def submit_query(self, query):
        self.llm_thread = threading.Thread(target=self.query_llm, args=(query,))
        self.llm_thread.start()
        response = self.llm_thread.join()
        return response

    def query_llm(self, query):
        result = self.llm.query(query)
        
        return result

    def query_scraper(self, url, use_robot_txt):
        if url != self.current_url:
            self.llm.reset_memory()
            self.current_url = url

        self.scraper.scrape(url, use_robot_txt)


def add_hyperlinks(sent):
    new_sent = copy.copy(sent)
    for token in sent.split(" "):
        if validators.url(token):
            href = f'<a href="{token}">{token}</a>'
            new_sent = new_sent.replace(token, href)

    return new_sent
