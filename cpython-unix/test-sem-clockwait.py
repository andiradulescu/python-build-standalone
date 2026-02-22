#!/usr/bin/env python3
"""Test that sem_clockwait is available and threading waits use monotonic clock.

Run against a python-build-standalone distribution to verify the weak symbol
patch is working:

    ./install/bin/python3 test-sem-clockwait.py

On Linux with glibc >= 2.30, sem_clockwait should be detected (either by
configure or via the weak symbol runtime check). On older glibc, the weak
symbol resolves to NULL and the fallback to sem_timedwait is used.
"""

import platform
import sys
import sysconfig
import threading
import time


def check_have_sem_clockwait():
    """Check if HAVE_SEM_CLOCKWAIT is set in the build configuration."""
    config_vars = sysconfig.get_config_vars()
    have = config_vars.get("HAVE_SEM_CLOCKWAIT")
    print(f"HAVE_SEM_CLOCKWAIT = {have!r}")
    if platform.system() == "Linux":
        if not have:
            print("FAIL: HAVE_SEM_CLOCKWAIT not set on Linux")
            return False
        print("OK: HAVE_SEM_CLOCKWAIT is set")
    else:
        print(f"SKIP: not Linux ({platform.system()})")
    return True


def check_event_wait_timing():
    """Sanity check that Event.wait returns in approximately the right time."""
    event = threading.Event()
    wait_sec = 0.1

    start = time.monotonic()
    result = event.wait(timeout=wait_sec)
    elapsed = time.monotonic() - start

    print(f"Event.wait({wait_sec}) returned {result} in {elapsed:.3f}s")

    if result:
        print("FAIL: Event.wait returned True (event was unexpectedly set)")
        return False

    # Allow generous bounds: 50ms to 2s
    if elapsed < 0.05:
        print(f"FAIL: returned too quickly ({elapsed:.3f}s < 0.05s)")
        return False
    if elapsed > 2.0:
        print(f"FAIL: took too long ({elapsed:.3f}s > 2.0s)")
        return False

    print("OK: timing is reasonable")
    return True


def main():
    print(f"Python {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print()

    ok = True
    ok = check_have_sem_clockwait() and ok
    print()
    ok = check_event_wait_timing() and ok
    print()

    if ok:
        print("All checks passed.")
    else:
        print("Some checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
