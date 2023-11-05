import threading
import time
from urllib.parse import urlparse

import html2text
from selenium import webdriver
from selenium.webdriver.common.by import By
import validators

def count_forward_slashes(url):
    return url.count("/")


def has_duplicate_https(url):
    return url.count("https://") > 1


class WebScraperConcurrent:
    def __init__(self, web_cache, vector_store, vector_lock, max_links=10, threads=3):
        self.max_links = max_links

        self.web_cache = web_cache
        self.cache_lock = threading.Lock()
        self.cache_connections = [None for _ in range(threads + 1)]

        self.vector_store = vector_store
        self.vector_lock = vector_lock

        self.visited_urls = set()
        self.unvisited_urls = []
        self.unvisited_lock = threading.Lock()

        driver_options = webdriver.ChromeOptions()
        driver_options.headless = True
        driver_options.add_argument("--headless=new")

        self.thread_drivers = [
            webdriver.Chrome(options=driver_options) for _ in range(threads + 1)
        ]

        # create initial thread
        self.threads = [
            threading.Thread(
                target=self.concurrent_scrape_data,
                kwargs={"first_page": True, "driver": self.thread_drivers[0]},
                name="t_0",
            )
        ]
        for i in range(threads):
            self.threads.append(
                threading.Thread(
                    target=self.concurrent_scrape_data,
                    kwargs={"driver": self.thread_drivers[i + 1]},
                    name="t_" + str(i + 1),
                )
            )

    def __exit__(self):
        print("Closing webdrivers")
        for driver in self.thread_drivers:
            driver.quit()

    def scrape(self, starting_url):
        print("Starting scrape process.")
        if starting_url[-1] != "/":
            starting_url = starting_url + "/"

        self.unvisited_urls.append(starting_url)

        self.threads[0].start()
        self.threads[0].join()

        for thread in self.threads[1:]:
            thread.start()

        for thread in self.threads[1:]:
            thread.join()

        return

    def concurrent_scrape_data(self, first_page=False, driver=None, cache_pool=None):
        """Scrapes data from website and subpages."""
        if driver is None:
            raise ValueError("No driver specified.")

        thread_name = threading.current_thread().name
        thread_id = int(thread_name.split("_")[-1])

        if not self.cache_connections[thread_id]:
            cache_connection = self.web_cache.get_connection()
            self.cache_connections[thread_id] = cache_connection

        self.unvisited_lock.acquire()
        while len(self.unvisited_urls) > 0 and len(self.visited_urls) < self.max_links:
            url = self.unvisited_urls.pop(0)
            if self.unvisited_lock.locked():
                self.unvisited_lock.release()

            if url not in self.visited_urls and not has_duplicate_https(url):
                valid_url = validators.url(url)
                if not valid_url:
                    continue

                self.visited_urls.add(url)

                cache_connection = self.cache_connections[thread_id]
                text, subpage_urls = self.web_cache.get_page(url, cache_connection)

                if not text:
                    print(f"Thread {thread_name} scraping {url}.")
                    cache = True
                    try:
                        driver.get(url)
                        text, subpage_urls = self.parse_html(url, driver)
                    finally:
                        pass
                else:
                    cache = False
                    print(f"Thread {thread_name} found {url} in cache.")

                self.store_results(
                    url, text, subpage_urls, cache_connection, cache=cache
                )

                if first_page:
                    break

        if self.unvisited_lock.locked():
            self.unvisited_lock.release()

        return

    def parse_html(self, url, driver):
        page_source = driver.page_source
        html_to_text = html2text.HTML2Text()
        html_to_text.ignore_links = True
        text = html_to_text.handle(page_source)

        href_links = driver.find_elements(By.XPATH, "//a[@href]")
        extracted_urls = set(link.get_attribute("href") for link in href_links)

        base_domain = urlparse(url).netloc
        subpage_urls = [
            link for link in extracted_urls if urlparse(link).netloc == base_domain
        ]

        return text, subpage_urls

    def store_results(self, url, text, subpage_urls, cache_connection, cache):
        thread_name = threading.current_thread().name
        thread_id = int(thread_name.split("_")[-1])
        subpage_urls_str = ";".join(subpage_urls)

        pages = [{"url": url, "text": text}]
        self.vector_store.add_pages(pages)

        if cache:
            cache_connection = self.cache_connections[thread_id]
            self.web_cache.add_page(url, text, subpage_urls_str, cache_connection)

        self.unvisited_lock.acquire()
        for subpage_url in subpage_urls:
            if (
                subpage_url not in self.visited_urls
                and subpage_url not in self.unvisited_urls
            ):
                self.unvisited_urls.append(subpage_url)
        self.unvisited_urls = sorted(self.unvisited_urls, key=count_forward_slashes)
        self.unvisited_lock.release()


if __name__ == "__main__":
    url = "https://www.bethanychurch.tv"

    threads = 3
    max_links = 10

    web_scraper = WebScraperConcurrent(max_links=max_links, threads=threads)
    start = time.time()
    web_scraper.scrape(url)
    end = time.time()
    print("Total time ", end - start)
