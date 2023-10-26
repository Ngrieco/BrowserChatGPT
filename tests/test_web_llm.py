from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper import WebScraper
from browserchatgpt.web_vectorstore import WebVectorStore

url = input("Enter URL for assistance: ")

web_scraper = WebScraper(max_links=3)

links, data = web_scraper.scrape_data_bfs_priority(url)
print(links)

web_data = WebVectorStore([data])

llm = WebLLM(web_data)

print("Feel free to ask anything.\n")
while True:
    query = input("User: ")
    result = llm.query(query)
    print("AI: ", result)
