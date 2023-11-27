import requests


def send_url_to_server(url):
    server_url = "http://127.0.0.1:5000/api/url"  # Update this URL if your server runs on a different address/port

    params = {"url": url}
    response = requests.get(server_url, params=params)

    if response.status_code == 200:
        data = response.json()
        success = data.get("success")
        print(f"Query Result: {success}")
    else:
        print("Error: Failed to get query result.")
        print("Code ", response.status_code)


def send_query_to_server(query):
    server_url = "http://127.0.0.1:5000/api/query"  # Update this URL if your server runs on a different address/port

    params = {"query": query}
    response = requests.get(server_url, params=params)

    if response.status_code == 200:
        data = response.json()
        response = data.get("response")
    else:
        print("Error: Failed to get query result.")
        print("Code ", response.status_code)

    return response


import time

url = "https://www.bethanychurch.tv"
send_url_to_server(url)

time.sleep(3)

url = "https://www.td.com/us/en/personal-banking"
send_url_to_server(url)


while True:
    query = input()
    response = send_query_to_server(query)
    print(response)
