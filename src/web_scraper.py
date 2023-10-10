from queue import PriorityQueue
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def count_forward_slashes(url):
    return url.count("/")


def has_duplicate_https(url):
    return url.count("https://") > 1


def is_same_path(url, previous_url):
    return urlparse(url).path == urlparse(previous_url).path


class WebScraper:
    def __init__(self, max_links=100, max_depth=2):
        self.max_links = max_links
        self.max_depth = max_depth

        driver_options = webdriver.SafariOptions()
        driver_options.headless = True
        driver_options.add_argument("--headless=new")
        self.driver = webdriver.Safari(options=driver_options)
        self.wait = WebDriverWait(self.driver, 10)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        print("Closing webdriver")
        self.driver.quit()

    def scrape_data_bfs_priority(self, starting_url):
        """Scrapes data from website and subpages

        Currently uses selenium and Safari. Safari can't
        run in headless mode. Plan to switch to Chrome
        for headless operation (faster). Uses a breadth first
        search and priority queue where we scrape higher
        sublinks (less forward slashes in url).
        """
        print("Starting search")
        visited_urls = set()  # Keep track of visited URLs using a set
        queue = PriorityQueue()
        gathered_links = set()
        data = []

        # Add the starting URL with depth 0
        queue.put((0, starting_url))

        while not queue.empty() and len(visited_urls) < self.max_links:
            current_depth, url = queue.get()
            if url not in visited_urls and not has_duplicate_https(url):
                try:
                    print("Currently scraping ", url)
                    self.driver.get(url)
                    # time.sleep(2)  # Give the page some time to load dynamically
                    visited_urls.add(url)  # Add the URL to the visited_urls set

                    """
                    # Set up a loop to scroll and load dynamic content
                    scroll_pause_time = 2  # Adjust the pause time as needed
                    last_height = self.driver.execute_script("return document.body.scrollHeight")

                    while True:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        WebDriverWait(self.driver, 10).until(
                            lambda driver: driver.execute_script("return document.body.scrollHeight") > last_height
                        )
                        last_height = self.driver.execute_script("return document.body.scrollHeight")
                        time.sleep(scroll_pause_time)  # Pause for a moment to allow content to load

                        # Break the loop when no more content is loaded
                        if last_height == self.driver.execute_script("return document.body.scrollHeight"):
                            break
                    """

                    # Extract the entire page's dynamic HTML content
                    dynamic_html = self.driver.page_source

                    file_path = "data.txt"
                    with open(file_path, "w") as file:
                        file.write(dynamic_html)
                    soup = BeautifulSoup(dynamic_html, "html.parser")
                    p_elements = soup.find_all("p")
                    for elem in p_elements:
                        if elem.text:
                            data.append(elem.text)
                            # print("- ", repr(elem.text.replace("\n", " ")))
                    # paragraph_elements = self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
                    # p_elements = self.driver.find_elements_by_tag_name("p")
                    # print("P ", p_elements)

                    # Extract all href links using find_elements with By.XPATH
                    href_links = self.driver.find_elements(By.XPATH, "//a[@href]")
                    extracted_urls = set(
                        link.get_attribute("href") for link in href_links
                    )

                    # Extract the base domain from the input URL
                    base_domain = urlparse(url).netloc

                    # Filter extracted URLs to keep only those within the same domain as the base URL
                    subpage_urls = [
                        link
                        for link in extracted_urls
                        if urlparse(link).netloc == base_domain
                    ]

                    # Assign priorities based on the number of forward slashes and add subpage URLs to the queue
                    for subpage_url in subpage_urls:
                        subpage_depth = count_forward_slashes(subpage_url)
                        queue.put((subpage_depth, subpage_url))

                    # Add the current URL to the gathered_links set
                    gathered_links.add(url)

                except Exception:
                    pass
                    # print(f"An error occurred: {e}")

        # return gathered_links
        return visited_urls, " ".join(data)


if __name__ == "__main__":
    url = "https://www.bethanychurch.tv"

    web_scraper = WebScraper(max_links=1)
    web_links, data = web_scraper.scrape_data_bfs_priority(url)
    print(data)
    for link in web_links:
        print(link)
