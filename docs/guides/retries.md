# Retries

Retries are centralized in the HTTPX2 transport. Safe requests retry transient transport
errors and status codes 408, 425, 429, 500, 502, 503, and 504. `Retry-After` seconds or HTTP
dates take precedence; otherwise bounded exponential full jitter applies.

Each request owns its retry loop. A failed symbol does not replay successful sibling requests.
Normal client errors, source schema errors, and quality errors are not retried.
