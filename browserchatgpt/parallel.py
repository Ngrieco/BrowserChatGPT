import multiprocessing
import os
import time
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def count_forward_slashes(url):
    return url.count("/")


def has_duplicate_https(url):
    return url.count("https://") > 1


def concurrent_scrape_data(url, url_queue, visited_urls, pages, driver):
    """Scrapes data from website and subpages

    Currently uses selenium and Chrome which runs
    in headless mode. Uses a breadth first
    search and priority queue where we scrape higher
    sublinks (less forward slashes in url).
    """

    print(f"Process ID: {os.getpid()} scraping {url}")

    # pages = []
    added_to_queue = []
    if url not in visited_urls and not has_duplicate_https(url):
        try:
            driver.get(url)

            # Extract the entire page's dynamic HTML content
            dynamic_html = driver.page_source
            html_to_text = html2text.HTML2Text()
            html_to_text.ignore_links = True
            text = html_to_text.handle(dynamic_html)

            pages.append({"url": url, "text": text})

            # Extract all href links using find_elements with By.XPATH
            href_links = driver.find_elements(By.XPATH, "//a[@href]")
            extracted_urls = set(
                link.get_attribute("href") for link in href_links
            )

            # Extract the base domain from the input URL
            base_domain = urlparse(url).netloc

            # Filter extracted URLs to keep only those within
            # the same domain as the base URL
            subpage_urls = [
                link
                for link in extracted_urls
                if urlparse(link).netloc == base_domain
            ]

            # Assign priorities based on the number of forward
            # slashes and add subpage URLs to the queue
            for subpage_url in subpage_urls:
                if (
                    subpage_url not in visited_urls
                    and subpage_url not in added_to_queue
                ):
                    # print(f"Process ID: {os.getpid()} adding {subpage_url}")
                    url_queue.put(subpage_url)
                    added_to_queue.append(subpage_url)

            # Add the URL to the visited_urls set
            visited_urls.append(url)

            # print(f"Process ID: {os.getpid()} visited\n {visited_urls}")

        except Exception as e:
            pass
    else:
        print("Not visiting ", url)

    return


def start_scraping(seed_urls, num_processes):
    with multiprocessing.Manager() as manager:
        url_queue = manager.Queue()
        visited_urls = manager.list()
        pages = manager.list()
        running_workers = manager.Value("i", num_processes)

        for url in seed_urls:
            url_queue.put(url)

        processes = []
        lock = manager.Lock()
        for _ in range(num_processes):
            process = multiprocessing.Process(
                target=worker,
                args=(url_queue, visited_urls, pages, running_workers, lock),
            )
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        print(len(visited_urls))
        for url in visited_urls:
            print(url)


driver_options = webdriver.ChromeOptions()
driver_options.headless = True
driver_options.add_argument("--headless=new")
max_urls = 20


# Worker function for each process
def worker(url_queue, visited_urls, pages, running_workers, lock):
    print(f"Starting Process ID: {os.getpid()}")

    driver = webdriver.Chrome(options=driver_options)

    while True:
        with lock:
            if (
                url_queue.empty()
                and running_workers.value <= 1
                or len(visited_urls) >= max_urls
            ):
                break

        if not url_queue.empty():
            url = url_queue.get()
            if url in visited_urls:
                continue

            # scrape_url(url, url_queue, visited_urls)
            concurrent_scrape_data(url, url_queue, visited_urls, pages, driver)
        else:
            # Sleep briefly if the queue is empty to avoid busy-waiting
            # print(f"Empty queue process ID: {os.getpid()} sleeping")

            time.sleep(1)

    print(f"Exiting Process ID: {os.getpid()}")


if __name__ == "__main__":
    seed_urls = ["https://www.bethanychurch.tv"]  # Add your initial URLs here
    num_processes = 1  # Number of parallel processes

    start = time.time()
    start_scraping(seed_urls, num_processes)
    end = time.time()
    print(f"Runtime for {max_urls} links is {end-start}")
