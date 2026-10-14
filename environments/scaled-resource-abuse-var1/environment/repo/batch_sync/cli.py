"""
CLI entrypoint for batch-sync.
"""
import argparse
import json
import os
import sys
from batch_sync import config
from batch_sync.dispatcher import dispatch_batch


def main():
    parser = argparse.ArgumentParser(description="Event Batch Synchronization Utility")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to JSON file containing list of events to dispatch",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=config.SUMMARY_OUTPUT_PATH,
        help="Destination path for sync summary JSON",
    )
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=config.MAX_CONCURRENCY,
        help=f"Maximum concurrent workers (default: {config.MAX_CONCURRENCY})",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file {args.input} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r") as f:
        events = json.load(f)

    if not isinstance(events, list):
        print("Error: input file must contain a JSON array of event objects", file=sys.stderr)
        sys.exit(1)

    summary = dispatch_batch(events, max_concurrency=args.concurrency, summary_path=args.output)
    print(f"Batch dispatch completed: {summary.get('delivered_count', 0)} / {len(events)} events delivered.")


if __name__ == "__main__":
    main()
