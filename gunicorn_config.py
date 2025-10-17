"""
Gunicorn configuration for Bees & Bears API.

Simple configuration using sync workers.
"""

import multiprocessing
import os

bind = "0.0.0.0:8000"

worker_class = "sync"
workers = int(os.getenv("GUNICORN_WORKERS", (multiprocessing.cpu_count() * 2) + 1))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))

accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

proc_name = "bees_and_bears_api"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
