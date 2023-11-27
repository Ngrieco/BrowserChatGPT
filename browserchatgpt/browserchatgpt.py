import threading
import copy
from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore
import validators

class BrowserChatGPT:
    def __init__(self):
        num_threads = 1
        max_links = 100
        database_name = "test_web_llm"
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

    def submit_url(self, requested_url):
        self.scraper_thread = threading.Thread(
            target=self.query_scraper, args=(requested_url,)
        )
        self.scraper_thread.start()

    def submit_query(self, query):
        self.llm_thread = threading.Thread(target=self.query_llm, args=(query,))
        self.llm_thread.start()
        response = self.llm_thread.join()
        return response

    def query_llm(self, query):
        result = self.llm.query(query)
        href_result = add_hyperlinks(result)

        return href_result

    def query_scraper(self, url):
        if(url != self.current_url):
            self.llm.reset_memory()
            self.current_url = url

        self.scraper.scrape(url)



def add_hyperlinks(sent):
    new_sent = copy.copy(sent)
    for token in sent.split(" "):
        if(validators.url(token)):
            href = f'<a href="{token}">{token}</a>'
            new_sent = new_sent.replace(token, href)

    return new_sent