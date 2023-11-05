import threading

from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore

num_threads = 3
max_links = 5
database_name = "test_web_llm"

pages = [{"url": "NA", "text": "Empty"}]

vs_lock = threading.Lock()

vector_store = WebVectorStore(pages, vs_lock)
cache = WebCache(database_name, num_threads)
llm = WebLLM(vector_store)

scraper = WebScraperConcurrent(
    cache, vector_store, vs_lock, max_links=max_links, threads=num_threads
)


def run_app(llm):
    print("Feel free to ask anything.\n")

    while True:
        query = input("User: ")
        result = llm.query(query)
        print("AI: ", result)


url = str(input("Enter URL for assistance: "))


# https://www.bethanychurch.tv
scrape_thread = threading.Thread(target=scraper.scrape, args=(url,))
llm_thread = threading.Thread(target=run_app, args=([llm]))

llm_thread.start()
scrape_thread.start()

# scraper.scrape(url)
