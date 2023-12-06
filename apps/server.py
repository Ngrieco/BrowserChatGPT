# Import necessary modules and classes
from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
import threading
import validators

# Import classes from custom modules
from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore

# Create a Flask web application
app = Flask(__name__)

# Define a class for the BrowserChatGPT application
class BrowserChatGPT():
    def __init__(self):
        num_threads = 3
        max_links = 100
        database_name = "web_llm"
        pages = [{"url": "NA", "text": "Empty"}]
        vs_lock = threading.Lock()
        # Initialize components for the application
        self.vector_store = WebVectorStore(pages, vs_lock)
        self.cache = WebCache(database_name, num_threads)
        self.llm = WebLLM(self.vector_store)
        self.scraper = WebScraperConcurrent(
            self.cache,
            self.vector_store,
            vs_lock,
            max_links=max_links,
            num_threads=num_threads,
        )

    # Method to submit a URL for scraping
    def submit_url(self, requested_url):
        thread = threading.Thread(target=self.query_scraper, args=(requested_url,))
        thread.start()

    # Method to submit a query to the language model
    def submit_query(self, query):
        thread = threading.Thread(target=self.query_llm, args=(query,))
        thread.start()

    # Method to query the language model
    def query_llm(self, query):
        result = self.llm.query(query)
        return result

    # Method to initiate URL scraping
    def query_scraper(self, url):
        self.scraper.scrape(url)

# Initialize the BrowserChatGPT application
chat_app = BrowserChatGPT()

# Endpoint for submitting a URL
@app.route('/submit_url', methods=['POST'])
def submit_url():
    data = request.get_json()
    chat_app.vector_store.reset()
    requested_url = "https://" + data['url']
    valid_url = validators.url(requested_url)
    if valid_url:
        try:
            chat_app.submit_url(requested_url)
            return jsonify({'status': 200, 'response': f'Hi, you are now chatting with {requested_url}!'})
        except Exception as e:
            return jsonify({'status': 401, 'response': f'Unable to load URL: {requested_url}.'})
    else:
        return jsonify({'status': 404, 'response': f'The URL: {requested_url} is invalid. Please restart and enter a valid URL.'})        

# Endpoint for submitting a query
@app.route('/submit_query', methods=['POST'])
def submit_query():
    data = request.get_json()
    query = data['query']
    result = chat_app.query_llm(query)
    return jsonify({'status': 200, 'response': result})

# Entry point to run the server using gevent for production
if __name__ == "__main__":
    http_server = WSGIServer(('', 8750), app)
    http_server.serve_forever()
