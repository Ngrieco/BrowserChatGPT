import threading
import time
from urllib import robotparser
from urllib.parse import urlparse

import html2text
import requests
import validators
from selenium import webdriver
from selenium.webdriver.common.by import By


def count_forward_slashes(url):
    return url.count("/")


def has_duplicate_https(url):
    return url.count("https://") > 1


class WebScraperConcurrent:
    def __init__(
        self, web_cache, vector_store, vector_lock, max_links=10, num_threads=3
    ):
        self.max_links = max_links

        self.web_cache = web_cache
        self.cache_lock = threading.Lock()
        self.cache_connections = [None for _ in range(num_threads + 1)]

        self.vector_store = vector_store
        self.vector_lock = vector_lock

        self.current_url = None
        self.visited_urls = set()
        self.unvisited_urls = []
        self.unvisited_lock = threading.Lock()

        self.robot_txt = None
        self.robot_txt_exists = False

        driver_options = webdriver.ChromeOptions()
        driver_options.headless = True
        driver_options.add_argument("--headless=new")

        self.num_threads = num_threads
        self.thread_drivers = [
            webdriver.Chrome(options=driver_options) for _ in range(num_threads + 1)
        ]

        self.threads = self.create_threads()

        self.running_threads = 0

    def __exit__(self):
        print("Closing webdrivers")
        for driver in self.thread_drivers:
            driver.quit()

    def create_threads(self):
        print("Creating threads")
        threads = [
            threading.Thread(
                target=self.concurrent_scrape_data,
                kwargs={"first_page": True, "driver": self.thread_drivers[0]},
                name="t_0",
            )
        ]
        for i in range(self.num_threads):
            threads.append(
                threading.Thread(
                    target=self.concurrent_scrape_data,
                    kwargs={"driver": self.thread_drivers[i + 1]},
                    name="t_" + str(i + 1),
                )
            )
        print(f"Created {len(threads)} new thread(s)")

        return threads

    def scrape(self, starting_url, use_robot_txt):
        self.use_robot_txt = use_robot_txt

        if starting_url[-1] != "/":
            starting_url = starting_url + "/"

        if not starting_url.startswith("https://"):
            # If "https://" is missing, add it
            starting_url = f"https://{starting_url}"

        # Resetting for scraping new website
        if starting_url != self.current_url:
            print(f"scrape new url {self.current_url} -> {starting_url}")

            if self.use_robot_txt:
                self.get_robot_txt(starting_url)

            self.current_url = starting_url
            self.visited_urls = set()
            self.unvisited_urls = []
            self.vector_store.clear()
            # self.vector_store.reset()

        print(f"Adding {starting_url} to the scrape queue.")

        # By only adding the starting url, if we were previously
        # scraping another website and changed sites, we remove
        # all previous URLs from the queue.
        self.unvisited_lock.acquire()
        self.unvisited_urls = [starting_url]
        self.unvisited_lock.release()

        if not self.running_threads:
            # Only start the threads one
            self.running_threads = 1
            # print("Thread 0")
            self.threads[0].start()
            self.threads[0].join()

            for i in range(1, self.num_threads + 1):
                # print(f"Starting thread {i}")
                self.threads[i].start()

            for i in range(1, self.num_threads + 1):
                # print(f"Joining thread {i}")
                self.threads[i].join()

        return

    def get_robot_txt(self, url):
        robots_url = f"{url}/robots.txt"
        response = requests.get(robots_url)
        if response.status_code == 200:  # Check if the file exists
            print("ROBOT_TXT EXISTS!!!")
            rp = robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.robot_txt = rp
            self.robot_txt_exists = True
        else:
            print("ROBOT_TXT DOESN'T EXIST!!!")
            self.robot_txt = None
            self.robot_txt_exists = False

    def concurrent_scrape_data(self, first_page=False, driver=None, cache_pool=None):
        """Scrapes data from website and subpages."""
        if driver is None:
            raise ValueError("No driver specified.")

        thread_name = threading.current_thread().name
        thread_id = int(thread_name.split("_")[-1])

        if not self.cache_connections[thread_id]:
            cache_connection = self.web_cache.get_connection()
            self.cache_connections[thread_id] = cache_connection

        while True:
            if len(self.visited_urls) >= self.max_links:
                print("SCRAPING TERMINATED - MAX LINKS LIMIT REACHED.")
                break

            self.unvisited_lock.acquire()
            if len(self.unvisited_urls) == 0:
                # if nothing to scrape, sleep and check later
                # print(f"Thread {thread_name} sleeping.")
                self.unvisited_lock.release()
                time.sleep(2)
                continue
            else:
                url = self.unvisited_urls.pop(0)
                self.unvisited_lock.release()

            if self.use_robot_txt and self.robot_txt_exists:
                is_blocked = self.robot_txt.can_fetch("browserchatgpt", url)
                if is_blocked:
                    print(f"Thread {thread_name} skipping {url} b/c robots_txt")
                    continue

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
    max_links = 6

    web_scraper = WebScraperConcurrent(max_links=max_links, threads=threads)
    start = time.time()
    web_scraper.scrape(url)
    end = time.time()
    print("Total time ", end - start)
