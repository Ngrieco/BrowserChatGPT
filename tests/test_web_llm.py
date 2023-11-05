from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_vector_store import WebVectorStore
import threading


num_threads = 3
database_name = "test_web_llm"

pages = [{"url": "NA", "text": "Empty"}]

vs_lock = threading.Lock()

vector_store = WebVectorStore(pages, vs_lock)
cache = WebCache(database_name, num_threads)
llm = WebLLM(vector_store)

scraper = WebScraperConcurrent(cache, vector_store, vs_lock, max_links=2, threads=num_threads)

url = input("Enter URL for assistance: ")
scraper.scrape(url)

# https://www.bethanychurch.tv
print("Feel free to ask anything.\n")
while True:
    query = input("User: ")
    result = llm.query(query)
    print("AI: ", result)
