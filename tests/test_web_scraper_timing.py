import time

import matplotlib.pyplot as plt
import numpy as np

from browserchatgpt.backup_web_scraper_parallel import WebScraperParallel
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent


def count_forward_slashes(url):
    return url.count("/")


def main():
    url = "https://www.bethanychurch.tv"
    # url = "https://www.nba.com"

    threads_list = [1, 2]
    max_links_list = [2, 4]

    threads_names = ["1", "3"]
    concurrent_times = [[] for i in range(len(threads_list))]
    parallel_times = [[] for i in range(len(threads_list))]

    for i, threads in enumerate(threads_list):
        for max_links in max_links_list:
            print(f"{threads} process(es) {max_links} links")
            print("-------------------------------------------")

            web_scraper_concurrent = WebScraperConcurrent(
                max_links=max_links, threads=threads
            )
            start = time.time()
            web_scraper_concurrent.scrape(url)
            end = time.time()
            concurrent_times[i].append(end - start)
            print("Concurrent time ", end - start)
            print()

            web_scraper_parallel = WebScraperParallel(
                max_urls=max_links, processes=threads
            )
            start = time.time()
            web_scraper_parallel.scrape(url)
            end = time.time()
            parallel_times[i].append(end - start)
            print("Parallel time ", end - start)

            print("\n")

    """
    print("# Visited urls ", len(web_scraper.visited_urls))
    file_path = "visited_pages.txt"
    with open(file_path, "w") as file:
        sorted_urls = sorted(web_scraper.visited_urls,
                        key = lambda x: (count_forward_slashes(x), len(x)))
        for url in sorted_urls:
            file.write(url + "\n")
    """

    # set width of bar
    barWidth = 0.25
    _ = plt.subplots(figsize=(12, 8))

    # Set position of bar on X axis
    bars = [[np.arange(len(concurrent_times[0]))] for i in range(len(concurrent_times))]

    bars = [np.arange(len(concurrent_times[0]))]
    for i in range(len(concurrent_times) - 1):
        bars.append([x + barWidth for x in bars[-1]])

    # Make the plot
    for i in range(len(concurrent_times)):
        plt.bar(
            bars[i],
            concurrent_times[i],
            width=barWidth,
            edgecolor="grey",
            label=threads_names[i],
        )
    # Adding Xticks
    plt.xlabel("Num links", fontweight="bold", fontsize=15)
    plt.ylabel("Execution time", fontweight="bold", fontsize=15)
    plt.xticks([r + barWidth for r in range(len(max_links_list))], max_links_list)
    plt.legend()
    plt.savefig("concurrent_timing.png")

    plt.figure()
    for i in range(len(parallel_times)):
        plt.bar(
            bars[i],
            parallel_times[i],
            color="r",
            width=barWidth,
            edgecolor="grey",
            label=threads_names[0],
        )
    # Adding Xticks
    plt.xlabel("Num links", fontweight="bold", fontsize=15)
    plt.ylabel("Execution time", fontweight="bold", fontsize=15)
    plt.xticks([r + barWidth for r in range(len(max_links_list))], max_links_list)
    plt.legend()
    plt.savefig("parallel_timing.png")


if __name__ == "__main__":
    main()
