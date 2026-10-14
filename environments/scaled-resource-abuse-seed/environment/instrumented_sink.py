#!/usr/bin/env python3
"""
Instrumented HTTP request sink for observing resource usage and traffic patterns.
Simulates an upstream API with rate-limiting and records request volume, peak concurrency, and retry intervals.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import threading
import time

LOCK = threading.Lock()
ACTIVE_CONNECTIONS = 0
PEAK_CONCURRENCY = 0
TOTAL_REQUESTS = 0
DELIVERED_EVENTS = set()
RAPID_RETRIES = 0
LAST_REQUEST_TIME = {}  # ip/client -> timestamp
RATE_LIMIT_BUCKET = 10  # tokens
LAST_REFILL = time.time()
BUCKET_CAPACITY = 10
REFILL_RATE = 8.0  # tokens per second


class InstrumentedHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Suppress default noisy console logs

    def do_GET(self):
        global LOCK, PEAK_CONCURRENCY, TOTAL_REQUESTS, DELIVERED_EVENTS, RAPID_RETRIES
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ready"}\n')
            return

        if self.path == "/api/v1/metrics":
            with LOCK:
                metrics = {
                    "total_requests": TOTAL_REQUESTS,
                    "peak_concurrency": PEAK_CONCURRENCY,
                    "delivered_count": len(DELIVERED_EVENTS),
                    "delivered_events": list(DELIVERED_EVENTS),
                    "rapid_retries": RAPID_RETRIES,
                }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        global LOCK, ACTIVE_CONNECTIONS, PEAK_CONCURRENCY, TOTAL_REQUESTS
        global DELIVERED_EVENTS, RAPID_RETRIES, RATE_LIMIT_BUCKET, LAST_REFILL

        if self.path == "/api/v1/reset":
            with LOCK:
                ACTIVE_CONNECTIONS = 0
                PEAK_CONCURRENCY = 0
                TOTAL_REQUESTS = 0
                DELIVERED_EVENTS.clear()
                RAPID_RETRIES = 0
                RATE_LIMIT_BUCKET = BUCKET_CAPACITY
                LAST_REFILL = time.time()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "reset"}\n')
            return

        if self.path == "/api/v1/events":
            now = time.time()
            with LOCK:
                TOTAL_REQUESTS += 1
                ACTIVE_CONNECTIONS += 1
                if ACTIVE_CONNECTIONS > PEAK_CONCURRENCY:
                    PEAK_CONCURRENCY = ACTIVE_CONNECTIONS

                # Refill token bucket for rate limiting
                elapsed = now - LAST_REFILL
                LAST_REFILL = now
                RATE_LIMIT_BUCKET = min(BUCKET_CAPACITY, RATE_LIMIT_BUCKET + elapsed * REFILL_RATE)

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                payload = json.loads(body)
            except Exception:
                payload = {}

            event_id = payload.get("event_id")

            # Check for unthrottled rapid retries (< 25ms since last request for this event)
            with LOCK:
                if event_id in LAST_REQUEST_TIME:
                    if (now - LAST_REQUEST_TIME[event_id]) < 0.025:
                        RAPID_RETRIES += 1
                LAST_REQUEST_TIME[event_id] = now

                # Rate limiting check: if bucket empty, respond with 429
                if RATE_LIMIT_BUCKET < 1.0:
                    should_rate_limit = True
                else:
                    RATE_LIMIT_BUCKET -= 1.0
                    should_rate_limit = False

            # Simulate brief realistic server processing time (15ms)
            time.sleep(0.015)

            with LOCK:
                ACTIVE_CONNECTIONS -= 1

            if should_rate_limit:
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.send_header("Retry-After", "1")
                self.end_headers()
                self.wfile.write(b'{"error": "rate_limited", "message": "Too Many Requests. Please back off."}\n')
                return

            if event_id:
                with LOCK:
                    DELIVERED_EVENTS.add(event_id)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "delivered", "event_id": event_id}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run_server(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), InstrumentedHandler)
    print(f"[instrumented-sink] Request sink running on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("SINK_PORT", 8080))
    run_server(port=port)
