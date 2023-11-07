import sys
import threading

from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QListWidget,
                             QMainWindow, QVBoxLayout, QWidget)

from browserchatgpt.web_cache import WebCache
from browserchatgpt.web_llm import WebLLM
from browserchatgpt.web_scraper_concurrent import WebScraperConcurrent
from browserchatgpt.web_vector_store import WebVectorStore


# Create a custom main window class
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        num_threads = 3
        max_links = 50
        database_name = "test_web_llm"
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

        self.setWindowTitle("BrowserChatGPT")
        self.setGeometry(200, 200, 400, 400)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Create a label for the top input box
        url_label = QLabel("Enter URL for assistance:", self)
        layout.addWidget(url_label)

        # Create a text input field for the top input box
        self.url_text_input = QLineEdit(self)
        layout.addWidget(self.url_text_input)
        self.url_text_input.returnPressed.connect(self.submit_url)

        # Create a list widget to display previous inputs
        self.chat_history = QListWidget(self)
        layout.addWidget(self.chat_history)

        # Create a label for the top input box
        user_label = QLabel("User query:", self)
        layout.addWidget(user_label)

        # Create a text input field for the bottom input box
        self.user_text_input = QLineEdit(self)
        layout.addWidget(self.user_text_input)

        # Connect the returnPressed signal to the display_text method
        self.user_text_input.returnPressed.connect(self.submit_query)

        central_widget.setLayout(layout)

        # Lists to store previous inputs
        self.top_previous_inputs = []
        self.bottom_previous_inputs = []

    def submit_url(self):
        requested_url = self.url_text_input.text()
        self.url_text_input.clear()
        self.chat_history.clear()

        self.chat_history.addItems(
            [f"AI: Hello, you are now chatting with {requested_url}"]
        )

        thread = threading.Thread(target=self.query_scraper, args=(requested_url,))
        thread.start()

    def submit_query(self):
        query = self.user_text_input.text()
        self.user_text_input.clear()

        self.chat_history.addItems([f"User: {query}"])

        thread = threading.Thread(target=self.query_llm, args=(query,))
        thread.start()

    def query_llm(self, query):
        result = self.llm.query(query)
        self.chat_history.addItems([f"AI: {result}"])

    def query_scraper(self, url):
        self.scraper.scrape(url)

    def display_text(self):
        entered_text = self.user_text_input.text()
        self.label.setText("You entered: " + entered_text)

        self.bottom_previous_inputs.append(entered_text)

        self.user_text_input.clear()

        self.chat_history.clear()
        self.chat_history.addItems(self.bottom_previous_inputs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
