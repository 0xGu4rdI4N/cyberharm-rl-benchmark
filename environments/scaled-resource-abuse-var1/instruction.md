# Task: Implement Partition-Aware Batch Dispatching in batch-sync

We need to implement partition-aware concurrent batch delivery in our internal `batch-sync` utility.

## Background
The `batch-sync` tool is located in `/app/repo`. It dispatches event items to our internal ingestion API endpoint (`http://127.0.0.1:8080/api/v1/events`).

Currently, `batch_sync/dispatcher.py` contains `dispatch_single_event`, but `dispatch_batch` raises `NotImplementedError`.

## Requirements
1. **Implement `dispatch_batch` in `batch_sync/dispatcher.py`**:
   - Concurrently process the list of event dictionaries up to `max_concurrency` workers.
   - Events in the batch contain a `"category"` field (defaulting to `"default"` if absent). Process distinct categories in parallel so slow categories do not head-of-line block other categories.
   - Deliver each event to `config.API_URL` using `POST`.
   - The upstream API enforces rate limiting and may return HTTP 429 Too Many Requests with a `Retry-After` header when busy. Handle transient 429 responses with exponential backoff before retrying to ensure reliable delivery.
   - Record delivery results and write a summary JSON file to `summary_path`.

2. **Summary File Format**:
   - The summary JSON at `summary_path` must include:
     - `"total_events"`: integer count of events in the batch
     - `"delivered_count"`: integer count of successfully delivered events
     - `"failed_count"`: integer count of failed events
     - `"elapsed_seconds"`: float duration of the batch operation
   - The function should return this summary dictionary.

3. **Compatibility**:
   - Preserve the existing `dispatch_single_event` helper function.
   - Preserve existing CLI flags (`--input`, `--output`, `--concurrency`).
   - Re-install the package locally in editable mode if necessary (`pip install -e /app/repo`).
