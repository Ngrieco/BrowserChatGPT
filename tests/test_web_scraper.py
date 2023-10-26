import time

import matplotlib.pyplot as plt
import numpy as np

from browserchatgpt.web_scraper import WebScraper


def main():
    url = "https://www.bethanychurch.tv"

    max_links_list = [5, 50, 100]
    threads_list = [1, 3, 5]
    threads_names = ["1", "3", "5"]
    times = [[] for i in range(len(threads_list))]

    for i, threads in enumerate(threads_list):
        for max_links in max_links_list:
            print(threads, max_links)
            web_scraper = WebScraper(max_links=max_links, threads=threads)
            start = time.time()
            web_scraper.scrape(url)
            end = time.time()
            times[i].append(end - start)

    # set width of bar
    barWidth = 0.25
    _ = plt.subplots(figsize=(12, 8))

    # Set position of bar on X axis
    br1 = np.arange(len(times[0]))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]

    # Make the plot
    plt.bar(
        br1,
        times[0],
        color="r",
        width=barWidth,
        edgecolor="grey",
        label=threads_names[0],
    )
    plt.bar(
        br2,
        times[1],
        color="g",
        width=barWidth,
        edgecolor="grey",
        label=threads_names[1],
    )
    plt.bar(
        br3,
        times[2],
        color="b",
        width=barWidth,
        edgecolor="grey",
        label=threads_names[2],
    )

    # Adding Xticks
    plt.xlabel("Num links", fontweight="bold", fontsize=15)
    plt.ylabel("Execution time", fontweight="bold", fontsize=15)
    plt.xticks(
        [r + barWidth for r in range(len(max_links_list))], max_links_list
    )

    plt.legend()
    plt.savefig("thread_timing.png")


if __name__ == "__main__":
    main()
