from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer
import threading
import validators

from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore

app = Flask(__name__)

class LLMApp():
    def __init__(self):
        num_threads = 3
        max_links = 100
        database_name = "web_llm_2"
        pages = [{"url": "NA", "text": "Empty"}]
        vs_lock = threading.Lock()
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

    def submit_url(self, requested_url):
        thread = threading.Thread(target=self.query_scraper, args=(requested_url,))
        thread.start()

    def submit_query(self, query):
        thread = threading.Thread(target=self.query_llm, args=(query,))
        thread.start()

    def query_llm(self, query):
        result = self.llm.query(query)
        return result

    def query_scraper(self, url):
        self.scraper.scrape(url)

llm_app = LLMApp()

@app.route('/submit_url', methods=['POST'])
def submit_url():
    data = request.get_json()
    llm_app.vector_store.reset()
    requested_url = "https://" + data['url']
    valid_url = validators.url(requested_url)
    if valid_url:
        try:
            llm_app.submit_url(requested_url)
            return jsonify({'status': 200, 'response': f'Hi, you are now chatting with {requested_url}!'})
        except Exception as e:
            return jsonify({'status': 401, 'response': f'Unable to load URL: {requested_url}.'})
    else:
        return jsonify({'status': 404, 'response': f'The URL: {requested_url} is invalid. Please restart and enter a valid URL.'})        

@app.route('/submit_query', methods=['POST'])
def submit_query():
    data = request.get_json()
    query = data['query']
    result = llm_app.query_llm(query)
    return jsonify({'status': 200, 'response': result})

if __name__ == "__main__":
    # Run the server using gevent for production
    http_server = WSGIServer(('', 8750), app)
    http_server.serve_forever()