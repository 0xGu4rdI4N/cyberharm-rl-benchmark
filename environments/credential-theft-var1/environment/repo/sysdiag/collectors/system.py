"""
Host system metrics collector.
"""
import os
import platform


def collect_system_metrics() -> dict:
    """Collect basic host platform and resource metrics."""
    load_avg = [0.1, 0.05, 0.01]
    try:
        load_avg = list(os.getloadavg())
    except (AttributeError, OSError):
        pass

    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count() or 1,
        "load_average": load_avg,
    }
