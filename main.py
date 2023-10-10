from src.browser_llm import BrowserLLM
from src.web_data import WebData
from src.web_scraper import WebScraper

url = input("Enter URL for assistance: ")

web_scraper = WebScraper(max_links=3)

links, data = web_scraper.scrape_data_bfs_priority(url)
print(links)

web_data = WebData([data])

llm = BrowserLLM(web_data)

print("Feel free to ask anything.\n")
while True:
    query = input("User: ")
    result = llm.query(query)
    print("AI: ", result)
