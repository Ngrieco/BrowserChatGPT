# Database cache of web data from most recently visited urls

import sqlite3
import threading
from datetime import datetime

CACHE_REFRESH_TIME_SECONDS = 60
MAX_SIZE_GB = 1
MAX_URLS = 50


class WebCache:
    def __init__(self, database_name="browserchatgpt", num_threads=1):
        self.database_name = database_name
        self.database_path = f"{database_name}.db"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"

        self.local_conn = sqlite3.connect(f"{database_name}.db", isolation_level=None)
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
        self.local_cursor.execute("PRAGMA auto_vacuum = 1;")

        self.cursor_edit_lock = threading.Lock()

    def get_connection(self):
        conn = sqlite3.connect(f"{self.database_name}.db", isolation_level=None)
        cursor = conn.cursor()
        return (conn, cursor)

    def add_page(self, url, text, subpage_urls_str, connection):
        conn, cursor = connection

        self.cursor_edit_lock.acquire()
        self.delete_excessive_storage(connection)

        current_time_str = datetime.now().strftime(self.datetime_format)

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

        self.delete_excessive_storage(connection)

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

    def get_size_mb(self, connection):
        # Execute query to fetch page size and page count
        _, cursor = connection
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]

        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]

        # Calculate database size in bytes and convert to megabytes
        database_size_kb = (page_size * page_count) / (1024 * 1024)
        print(f"SQLite database size: {database_size_kb:.2f} MB")

        return database_size_kb

    def delete_excessive_storage(self, connection):
        conn, cursor = connection
        while self.get_size_mb(connection) > MAX_SIZE_GB:
            cursor.execute("SELECT url FROM pages ORDER BY timestamp LIMIT 1;")
            oldest_entry = cursor.fetchone()
            print("Oldest entry ", oldest_entry)

            # If an oldest entry exists, delete it
            if oldest_entry:
                delete_query = f"""
                    DELETE FROM pages
                    WHERE url = '{oldest_entry[0]}';
                """
                cursor.execute(delete_query)
                print("Oldest entry deleted successfully")

                cursor.execute("VACUUM;")

            # Commit the changes
            conn.commit()


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
