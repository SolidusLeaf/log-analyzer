import threading
import queue
import os
# WARNING: Number of worker threads should be adjusted based on system capabilities NOT buffer size.
# Too many threads can lead to high CPU usage and system instability, especially if the log processing is resource-intensive.
# Current number of threads is set to 10 for safety, but can be increased for faster processing on powerful systems. 

# Monitor CPU usage when adjusting is adviced.


MAX_BUFFER_SIZE = 50 # max number of log lines in buffer
MAX_NUM_WORKERS = 10 # number of worker threads to process log lines - adjust based on system capabilities

lock = threading.Lock() # lock for synchronizing access to shared resources (like results dictionary)
while True:
    num_workers=input(f"Enter the number of worker threads (1-{MAX_NUM_WORKERS}): ")
    try:
        num_workers = int(num_workers)
        if 1 <= num_workers <= MAX_NUM_WORKERS:
            break
        else:
            print(f"Please enter a number between 1 and {MAX_NUM_WORKERS}.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
while True:
    buffer_size=input(f"Enter the buffer size (1-{MAX_BUFFER_SIZE}): ")
    try:
        buffer_size = int(buffer_size)
        if 1 <= buffer_size <= MAX_BUFFER_SIZE and buffer_size >= num_workers:
            break
        else:
            print(f"Please enter a number between 1 and {MAX_BUFFER_SIZE} that is also greater than or equal to the number of worker threads.")
            print(f"Current number of worker threads: {num_workers}.")
            print("\t==Optimal buffer size ratio is usually 1:1 or 1:2-5 (worker:buffer) for better performance==")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

q=queue.Queue(maxsize=buffer_size)
results = {
    "error": 0,
    "warning": 0,
    "failed": 0,
    "error_lines": [],
    "warning_lines": [],
    "failed_lines": []
}
def reader(file_path):
    with open(file_path, "r") as f:
        for idx, line in enumerate(f, start=1):
            q.put((idx, line))   # line number and line content for observability

    for _ in range(num_workers):
        q.put(None) # Update status for worker threads to stop after processing all lines


def worker():
    while True:
        item = q.get()

        if item is None:
            q.task_done() # Safety measure to prevent deadlock if workers are waiting on the queue
            break

        line_num, line = item
        text = line.lower()

        keys = []

        if "error" in text:
            keys.append("error")
        if "warning" in text:
            keys.append("warning")
        if "failed" in text:
            keys.append("failed")

        if keys:
            lock.acquire()
            try:
                for key in keys:
                    results[key] += 1
                    results[f"{key}_lines"].append(line_num)
            finally:
                lock.release()
        q.task_done() # Mark the task as done after processing the line


def print_report():
    print("\n" + "="*42)
    print("           LOG ANALYSIS REPORT")
    print("="*42)

    def show(title, key):
        lines = results.get(key, [])
        print(f"\n{title}: {len(lines)}")
        print(", ".join(map(str, lines[:20])) or "No occurrences found.")

        remaining = max(0, len(lines) - 20)
        if remaining > 0:
            print(f"... +{remaining} more")

    print(f"\nErrors  : {results.get('error', 0)}")
    print(f"Warnings: {results.get('warning', 0)}")
    print(f"Failed  : {results.get('failed', 0)}")

    show("ERROR LOCATIONS", "error_lines")
    show("WARNING LOCATIONS", "warning_lines")
    show("FAILED LOCATIONS", "failed_lines")

    print("\n" + "="*42)



if __name__ == "__main__":

    # --- file validation ---
    while True:
        file_path = input("Enter the path to the log file: ")

        if os.path.isfile(file_path):
            print(f"File found: {file_path}")
            break
        else:
            print("Invalid file path. Try again.")

    # --- start workers ALWAYS FIRST ---
    worker_threads = []
    for _ in range(num_workers):
        t = threading.Thread(target=worker)
        t.start()
        worker_threads.append(t)

    # --- start reader AFTER starting workers ---
    reader_thread = threading.Thread(target=reader, args=(file_path,))
    reader_thread.start()

    # --- synchronization ---
    reader_thread.join()
    q.join()

    for t in worker_threads:
        t.join()

    # --- output ---
        print_report()
        print("\nNote: A single line can contain multiple keywords (error, warning, failed) and will be counted in each category.")
