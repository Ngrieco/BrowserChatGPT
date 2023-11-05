# Database cache of web data from most recently visited urls
import os
import sqlite3

from datetime import datetime
import threading

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
        
        #print("add_page acquire")
        self.cursor_edit_lock.acquire()
        if not self.is_page_cached(url, connection, lock=False) or self.is_page_stale(url, connection, lock=False):
            #print(f"Caching {url}")
            
            if(self.is_page_stale(url, connection, lock=False)):
                #print("Deleting stale page")
                self.delete_page(url, connection)

            cursor.execute(
                "INSERT INTO pages (url, timestamp, subpage_urls, text) VALUES (?, ?, ?, ?)",
                (url, current_time_str, subpage_urls_str, text),
            )
            conn.commit()
        else:
            pass
            #print(f"{url} is already cached.")

        #print("add_page release")
        self.cursor_edit_lock.release()

    def get_page(self, url, connection):
        _, cursor = connection

        self.cursor_edit_lock.acquire()
        if self.is_page_cached(url, connection, lock=False):
            cursor.execute("SELECT url, text, subpage_urls FROM pages WHERE url=?", (url,))
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
        '''lock should only be set to true when running the function
        as a standalone function. '''
        _, cursor = connection
        
        if lock:
            #print("is_page_cached acquire")
            self.cursor_edit_lock.acquire()
            cursor.execute("SELECT url FROM pages WHERE url=?", (url,))
            result = cursor.fetchone()
            #print("is_page_cached release")
            self.cursor_edit_lock.release()
        else:
            cursor.execute("SELECT url FROM pages WHERE url=?", (url,))
            result = cursor.fetchone()

        return result

    def is_page_stale(self, url, connection, lock=True):
        _, cursor = connection

        if self.is_page_cached(url, connection, lock=False):
            if lock:
                #print("is_page_stale acquire")
                self.cursor_edit_lock.acquire()
                cursor.execute("SELECT url, timestamp FROM pages WHERE url=?", (url,))
                result = cursor.fetchone()
                #print("is_page_stale release")
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

    def is_space_for_page(self, text):
        encoded_string = text.encode("utf-8")
        size_in_bytes = len(encoded_string)
        print(f"Trying to add string of size {size_in_bytes}")

    def delete_excessive_storage(self):
        current_db_size = self.get_db_size()

        if current_db_size > MAX_SIZE_BYTES:
            print("Deleting excess")
            # Determine how many bytes to free up
            bytes_to_free_up = current_db_size - MAX_SIZE_BYTES

            # Sort entries by timestamp (replace 'timestamp' with your timestamp column name)
            self.cursor.execute("SELECT url, LENGTH(text) FROM pages ORDER BY timestamp")
            entries_to_delete = self.cursor.fetchall()
            freed_bytes = 0

            # Delete the oldest entries to free up space
            for entry in entries_to_delete:
                url_to_delete, text_length = entry[0], entry[1]
                bytes_freed = text_length
                self.cursor.execute("DELETE FROM pages WHERE url=?", (url_to_delete,))
                freed_bytes += bytes_freed
                print(f"Bytes freed {freed_bytes}")
                if freed_bytes >= bytes_to_free_up:
                    break

            # Commit the changes
            self.conn.commit()


if __name__ == "__main__":
    web_cache_database = WebCache("test")
    connection = web_cache_database.get_connection()

    num_entries = 10
    for i in range(num_entries):
        url = f"google{i}.com"
        text = f"Hello World {i}"
        web_cache_database.add_page(url, text, "", connection)

    url = f"google{num_entries+1}.com"
    text = f"Hello World {num_entries+1}"
    web_cache_database.add_page(url, text, "", connection)
