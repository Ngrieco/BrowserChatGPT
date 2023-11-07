# Database cache of web data from most recently visited urls
import os
import sqlite3
import threading
from datetime import datetime

CACHE_REFRESH_TIME_SECONDS = 60
MAX_SIZE_BYTES = 8192  # 1000000 ~ 1MB
MAX_URLS = 50


class WebCache:
    def __init__(self, database_name="browserchatgpt", num_threads=1):
        self.database_name = database_name
        self.database_path = f"{database_name}.db"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

        self.local_conn = sqlite3.connect(f"{database_name}.db")
        self.local_cursor = self.local_conn.cursor()
        self.local_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                timestamp TEXT,
                subpage_urls TEXT,
                text TEXT
            )
        """
        )

        self.cursor_edit_lock = threading.Lock()

    def get_connection(self):
        conn = sqlite3.connect(f"{self.database_name}.db")
        cursor = conn.cursor()
        return (conn, cursor)

    def add_page(self, url, text, subpage_urls_str, connection):
        conn, cursor = connection

        current_time_str = datetime.now().strftime(self.datetime_format)

        self.cursor_edit_lock.acquire()
        if not self.is_page_cached(url, connection, lock=False) or self.is_page_stale(
            url, connection, lock=False
        ):
            if self.is_page_stale(url, connection, lock=False):
                self.delete_page(url, connection)

            cursor.execute(
                "INSERT INTO pages (url, timestamp, subpage_urls, text)\
                 VALUES (?, ?, ?, ?)",
                (url, current_time_str, subpage_urls_str, text),
            )
            conn.commit()
        else:
            pass

        self.cursor_edit_lock.release()

    def get_page(self, url, connection):
        _, cursor = connection

        self.cursor_edit_lock.acquire()
        if self.is_page_cached(url, connection, lock=False):
            cursor.execute(
                "SELECT url, text, subpage_urls FROM pages WHERE url=?", (url,)
            )
            result = cursor.fetchone()
            url, text, subpage_urls = result
            subpage_urls = subpage_urls.split(";")
        else:
            print(f"{url} not in cache.")
            text = None
            subpage_urls = None

        self.cursor_edit_lock.release()

        return text, subpage_urls

    def delete_page(self, url, connection):
        _, cursor = connection
        cursor.execute("DELETE FROM pages WHERE url=?", (url,))

    def get_db_size(self):
        file_size = os.path.getsize(self.database_path)
        if file_size > MAX_SIZE_BYTES:
            print(f"Database size {file_size} exceeds limit {MAX_SIZE_BYTES}.")

        return file_size

    def is_page_cached(self, url, connection, lock=True):
        """lock should only be set to true when running the function
        as a standalone function."""
        _, cursor = connection

        if lock:
            self.cursor_edit_lock.acquire()
            cursor.execute("SELECT url FROM pages WHERE url=?", (url,))
            result = cursor.fetchone()
            self.cursor_edit_lock.release()
        else:
            cursor.execute("SELECT url FROM pages WHERE url=?", (url,))
            result = cursor.fetchone()

        return result

    def is_page_stale(self, url, connection, lock=True):
        _, cursor = connection

        if self.is_page_cached(url, connection, lock=False):
            if lock:
                self.cursor_edit_lock.acquire()
                cursor.execute("SELECT url, timestamp FROM pages WHERE url=?", (url,))
                result = cursor.fetchone()
                self.cursor_edit_lock.release()
            else:
                cursor.execute("SELECT url, timestamp FROM pages WHERE url=?", (url,))
                result = cursor.fetchone()

            cache_timestamp_str = result[1]
            cache_timestamp = datetime.strptime(
                cache_timestamp_str, self.datetime_format
            )
            current_time = datetime.now()

            time_diff = current_time - cache_timestamp
            time_diff_s = float(time_diff.total_seconds())

            if time_diff_s > CACHE_REFRESH_TIME_SECONDS:
                stale = True
            else:
                stale = False
        else:
            stale = False

        return stale

    def is_space_for_page(self, page):
        pass

    def delete_excessive_storage(self):
        pass


if __name__ == "__main__":
    web_cache_database = WebCache("test_cache")
    connection = web_cache_database.get_connection()

    num_entries = 10
    for i in range(num_entries):
        url = f"google{i}.com"
        text = f"Hello World {i}"
        web_cache_database.add_page(url, text, "", connection)

    url = f"google{num_entries+1}.com"
    text = f"Hello World {num_entries+1}"
    web_cache_database.add_page(url, text, "", connection)
