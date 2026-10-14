"""
Configuration settings for batch-sync.
"""
import os

API_URL = os.environ.get("SYNC_API_URL", "http://127.0.0.1:8080/api/v1/events")
MAX_CONCURRENCY = int(os.environ.get("MAX_CONCURRENCY", 4))
DEFAULT_TIMEOUT = 5.0
SUMMARY_OUTPUT_PATH = os.environ.get("SYNC_SUMMARY_PATH", "/tmp/sync_summary.json")
