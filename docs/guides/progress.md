# Progress

Pass `progress=True` for terminal/notebook text, a callback for typed events, or a custom
`ProgressReporter`.

```python
events = []
df = ox.daily_prices(["فولاد"], progress=events.append)
```

Transfers with `Content-Length` expose a real percentage and finish at exactly 100%. Unknown
lengths report bytes and throughput without inventing a percentage. Batch progress counts
completed items and exposes retries and failures.
