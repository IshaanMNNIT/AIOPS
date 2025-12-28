import time
from collections import defaultdict


class RateLimitError(Exception):
    pass


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)

    def check(self, key: str):
        now = time.time()
        window_start = now - self.window

        timestamps = [
            t for t in self.requests[key] if t > window_start
        ]

        if len(timestamps) >= self.max_requests:
            raise RateLimitError("Rate limit exceeded")

        timestamps.append(now)
        self.requests[key] = timestamps
