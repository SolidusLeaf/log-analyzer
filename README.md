# Log Analysis Tool (Multithreaded Pipeline)

A lightweight multithreaded log processing tool that analyzes large log files and extracts occurrences of key keywords such as `error`, `warning`, and `failed`.

---
## Features

- Multithreaded worker pipeline (producer–consumer model)
- Buffered processing using thread-safe queue
- Configurable number of worker threads
- Configurable buffer size (backpressure control)
- Detects:
    - Errors
    - Warnings
    - Failures
- Tracks line numbers for traceability
- Thread-safe aggregation using locks
- Graceful completion after processing all data
---
## How it works

The system is built as a **two-stage pipeline**:

### 1. Reader (Producer)

- Reads file line by line
- Pushes `(line_number, line)` into a shared queue
- Sends termination signals (`None`) to workers

### 2. Workers (Consumers)

Each worker:

- Pulls data from queue
- Analyzes text for keywords
- Updates shared statistics safely using a lock

### 3. Aggregation

- Counts occurrences per category
- Stores line numbers for each match
- Produces final report after completion
---
## Usage

Run the script:

```bash
python log_analyzer.py
```

Then follow prompts:
```
Enter the path to the log file: /path/to/log.txt  
Enter number of worker threads (1-10): 5  
Enter buffer size (1-50): 20
```
---
## Example output
```
==========================================
           LOG ANALYSIS REPORT
==========================================

Errors  : 12
Warnings: 7
Failed  : 4

ERROR LOCATIONS: 12
3, 10, 15, 22, 31, ...

WARNING LOCATIONS: 7
5, 9, 14, ...

FAILED LOCATIONS: 4
8, 19, 27, ...
```
---
## Architecture

- Producer–Consumer pattern
- `queue.Queue` as synchronization buffer
- Thread pool of workers
- Lock-based shared state protection
- Poison-pill shutdown (`None` signals)
---
## Requirements  
  
- Python 3.8+  
- Standard Library only:  
- threading  
- queue  
- os
---
## Design notes

- Buffer size must be ≥ worker count (prevents starvation)
- Lock is used only for aggregation (minimizes contention)
- Queue acts as backpressure control system
- Poison pills ensure clean shutdown
---
## Limitations

- Keyword-based detection (no semantic parsing)
- Single-file processing only
- No streaming multi-file ingestion
- CPU-bound for very large logs
- No async I/O or multiprocessing support
---
## Motivation

This project was built to practice:

- multithreaded systems design
- producer–consumer pipelines
- shared memory synchronization
- scalable log processing patterns
- controlled concurrency via queue + semaphore logic
