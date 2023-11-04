import multiprocessing
import os
import threading
import time
from urllib.parse import urlparse

import html2text
from selenium import webdriver
from selenium.webdriver.common.by import By

max_urls = 20
num_processes = 3

driver_options = webdriver.ChromeOptions()
driver_options.headless = True
driver_options.add_argument("--headless=new")
print(f"Process ID: {os.getpid()} creating driver")
driver = webdriver.Chrome(options=driver_options)
print(f"Process ID: {os.getpid()} done creating driver")

def count_forward_slashes(url):
    return url.count("/")

def has_duplicate_https(url):
    return url.count("https://") > 1

class WebScraper:
    def __init__(self, max_links=100, processes=1):
        self.max_links = max_links
        self.num_processes = processes

        driver_options = webdriver.ChromeOptions()
        driver_options.headless = True
        driver_options.add_argument("--headless=new")


    def __exit__(self):
        print("Closing webdrivers")
        for driver in self.drivers:
            driver.quit()

    def scrape(self, url):
        pages = parallel_scrape(url, self.num_processes)
        return pages


def parallel_scrape(url, num_processes):
    with multiprocessing.Manager() as manager:
        processes = []
        lock = manager.Lock()
        pages = manager.list()
        url_queue = manager.Queue()
        visited_urls = manager.list()
        running_workers = manager.Value("i", num_processes)

        url_queue.put(url)
        for i in range(num_processes):
            
            # create parallel scraping workers
            process = multiprocessing.Process(
                target=scrape_worker,
                args=(
                    url_queue,
                    visited_urls,
                    pages,
                    running_workers,
                    lock,
                ),
                name=f"process_{i}"
            )

            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        return pages

def scrape_data(url, url_queue, visited_urls, pages):
    """Scrapes data from website and subpages

    Currently uses selenium and Chrome which runs
    in headless mode. Uses a breadth first
    search and priority queue where we scrape higher
    sublinks (less forward slashes in url).
    """
    print(f"Process ID: {os.getpid()} scraping {url}")


    global driver
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
                    #print(f"Process ID: {os.getpid()} adding {subpage_url}")
                    url_queue.put(subpage_url)
                    added_to_queue.append(subpage_url)

            # Add the URL to the visited_urls set
            visited_urls.append(url)

            # print(f"Process ID: {os.getpid()} visited\n {visited_urls}")

        except Exception as e:
            print(e)
    else:
        print("Not visiting ", url)

    return

def scrape_worker(url_queue, visited_urls, pages, running_workers, lock):
    #driver_id = int(multiprocessing.current_process().name.split("_")[-1])


    print(f"Starting Process ID: {os.getpid()}")
    while True:

        lock.acquire()
        if (
            url_queue.empty()
            and running_workers.value <= 1
            or len(visited_urls) >= max_urls
        ):
            break

        if not url_queue.empty():
            url = url_queue.get()
            lock.release()

            if url in visited_urls:
                continue

            # scrape_url(url, url_queue, visited_urls)
            scrape_data(url, url_queue, visited_urls, pages)
        else:
            # Sleep briefly if the queue is empty to avoid busy-waiting
            # print(f"Empty queue process ID: {os.getpid()} sleeping")
            lock.release()
            time.sleep(1)


    lock.release()

    print(f"Exiting Process ID: {os.getpid()}")



if __name__ == "__main__":
    



    print("Hello World")

    url = "https://www.bethanychurch.tv"

    web_scraper = WebScraper(max_links=max_urls, processes=num_processes)
    
    start = time.time()
    web_scraper.scrape(url)
    end = time.time()

    
    print("Total time ", end - start)

