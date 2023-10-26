import threading
from urllib.parse import urlparse

import html2text
from selenium import webdriver
from selenium.webdriver.common.by import By


def count_forward_slashes(url):
    return url.count("/")


def has_duplicate_https(url):
    return url.count("https://") > 1


class WebScraper:
    def __init__(self, max_links=100, threads=1):
        self.max_links = max_links

        self.visited_urls = set()

        self.unvisited_lock = threading.Lock()
        self.unvisited_urls = []

        self.pages_lock = threading.Lock()

        driver_options = webdriver.ChromeOptions()
        driver_options.headless = True
        driver_options.add_argument("--headless=new")

        self.general_driver = webdriver.Chrome(options=driver_options)
        self.initial_thread = threading.Thread(
            target=self.concurrent_scrape_data,
            kwargs={"first_page": True, "driver": self.general_driver},
            name="init_thread",
        )

        self.thread_drivers = [
            webdriver.Chrome(options=driver_options) for _ in range(threads)
        ]
        self.threads = [
            threading.Thread(
                target=self.concurrent_scrape_data,
                kwargs={"driver": self.thread_drivers[thread]},
                name="t" + str(thread),
            )
            for thread in range(threads)
        ]

    def __exit__(self):
        print("Closing webdrivers")
        self.general_driver.quit()
        for driver in self.thread_drivers:
            driver.quit()

    def concurrent_scrape_data(self, first_page=False, driver=None):
        """Scrapes data from website and subpages

        Currently uses selenium and Chrome which runs
        in headless mode. Uses a breadth first
        search and priority queue where we scrape higher
        sublinks (less forward slashes in url).
        """

        if driver is None:
            raise ValueError("No driver specified.")

        pages = []

        self.unvisited_lock.acquire()
        while (
            len(self.unvisited_urls) > 0
            and len(self.visited_urls) < self.max_links
        ):
            url = self.unvisited_urls.pop(0)

            if self.unvisited_lock.locked():
                self.unvisited_lock.release()
                # print(f"Thread {threading.current_thread().name} unlocking")

            if url not in self.visited_urls and not has_duplicate_https(url):
                try:
                    driver.get(url)

                    # Add the URL to the visited_urls set
                    self.visited_urls.add(url)

                    # Extract the entire page's dynamic HTML content
                    dynamic_html = driver.page_source

                    html_to_text = html2text.HTML2Text()
                    html_to_text.ignore_links = True
                    text = html_to_text.handle(dynamic_html)

                    self.pages_lock.acquire()
                    pages.append({"url": url, "text": text})
                    self.pages_lock.release()

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
                    self.unvisited_lock.acquire()
                    for subpage_url in subpage_urls:
                        if (
                            subpage_url not in self.visited_urls
                            and subpage_url not in self.unvisited_urls
                        ):
                            self.unvisited_urls.append(subpage_url)

                    self.unvisited_urls = sorted(
                        self.unvisited_urls, key=count_forward_slashes
                    )
                    self.unvisited_lock.release()

                    if first_page:
                        break

                finally:
                    pass

        if self.unvisited_lock.locked():
            self.unvisited_lock.release()

        return

    def scrape(self, starting_url):
        if starting_url[-1] != "/":
            starting_url = starting_url + "/"

        self.unvisited_urls.append(starting_url)

        self.initial_thread.start()
        self.initial_thread.join()

        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()
