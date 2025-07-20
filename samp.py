import os
import sqlite3
import hashlib
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification
import tkinter as tk
from tkinter import messagebox

# Function to compute file hash (SHA-256)
def compute_file_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
    except Exception as e:
        print(f"Error computing hash for {filepath}: {e}")
    return sha256.hexdigest()

# Function to check for duplicates
def check_for_duplicates(cursor, filename, filesize, filehash):
    try:
        cursor.execute("SELECT * FROM downloads WHERE (filename=? OR filehash=?) AND filesize=?", (filename, filehash, filesize))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error checking for duplicates: {e}")
        return None

# Function to log new downloads
def log_download(cursor, filename, filesize, filehash):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute("INSERT INTO downloads (filename, filesize, filehash, timestamp) VALUES (?, ?, ?, ?)",
                       (filename, filesize, filehash, timestamp))
    except Exception as e:
        print(f"Error logging download: {e}")

# Function to open the Downloads folder
def open_downloads_folder():
    download_dir = os.path.expanduser("~/Downloads")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{download_dir}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", download_dir])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", download_dir])
    except Exception as e:
        print(f"Error opening Downloads folder: {e}")

# Handler for monitoring file downloads
class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            filepath = event.src_path
            filename = os.path.basename(filepath)
            
            # Check if the file still exists before proceeding
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return

            try:
                filesize = os.path.getsize(filepath)
            except FileNotFoundError:
                print(f"File not found: {filepath}")
                return
            except Exception as e:
                print(f"Error accessing file size: {e}")
                return

            filehash = compute_file_hash(filepath)

            # Establish a new database connection in this thread
            conn = sqlite3.connect('downloads_metadata.db')
            cursor = conn.cursor()

            # Check if the file is a duplicate
            duplicate = check_for_duplicates(cursor, filename, filesize, filehash)
            if duplicate:
                # Move the file to a temporary location to "pause" the download
                temp_path = filepath + ".tmp"
                shutil.move(filepath, temp_path)

                msg = (f"Duplicate file detected!\n"
                       f"Filename: {duplicate[1]}\n"
                       f"Size: {duplicate[2]} bytes\n"
                       f"Location: {os.path.join(os.path.expanduser('~/Downloads'), duplicate[1])}\n"  # Assuming the original download location
                       f"Timestamp: {duplicate[4]}\n\n"
                       "Do you want to keep this new download?")
                
                # Display a system notification
                notification.notify(
                    title="Duplicate Download Alert",
                    message=f"Duplicate detected: {duplicate[1]} at {os.path.join(os.path.expanduser('~/Downloads'), duplicate[1])}",
                    app_name="DDAS",
                    timeout=10
                )
                
                # Prompt the user with a yes/no dialog box
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                response = messagebox.askyesno("Duplicate Download Alert", msg)
                root.destroy()

                if not response:
                    os.remove(temp_path)
                    print(f"Duplicate download removed: {filename}")
                    conn.close()
                    return
                else:
                    # Move the file back to its original location
                    shutil.move(temp_path, filepath)

            # Log the download if it's not a duplicate or if the user decides to keep it
            log_download(cursor, filename, filesize, filehash)
            conn.commit()
            conn.close()
            print(f"New file downloaded and logged: {filename}")

# Function to monitor the download directory
def monitor_downloads(download_directory):
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, download_directory, recursive=False)
    observer.start()
    print(f"Monitoring downloads in: {download_directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Initialize the database connection and create the table (if not already created)
conn = sqlite3.connect('downloads_metadata.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filesize INTEGER NOT NULL,
    filehash TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')
conn.commit()
conn.close()

# Specify the directory to monitor (default download directory)
download_directory = os.path.expanduser("~/Downloads")
monitor_downloads(download_directory)
