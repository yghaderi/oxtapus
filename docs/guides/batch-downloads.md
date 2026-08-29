# Batch downloads

`Settings(concurrency=4)` bounds simultaneous work. Sync uses a thread pool around native sync
requests; async uses a semaphore around native async requests. `FailureMode.COLLECT` returns
successful rows and records item failures in `FetchResult`; `FAIL_FAST` stops on the first
error.
