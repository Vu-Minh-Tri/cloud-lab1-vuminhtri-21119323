"""Lab 02 — Distributed Client-Server Application (TCP client).

Tasks covered:
  Task 1: Connect to 127.0.0.1:5000, send "Hello from client!", and display
          the server's response.
  Task 3: A 2-second socket timeout is set; if the server delays longer than
          that, the client catches TimeoutError and reports it gracefully
          instead of crashing.
  Task 4: Bounded retry with exponential backoff — at most 3 attempts,
          waiting 0.5 s before attempt 2 and 1 s before attempt 3.

Usage:
    python client.py                 # normal run (retry/backoff enabled)
    python client.py --no-retry      # single attempt only (Task 1/3 demos)

Standard library only; runs on localhost — no cloud account required.
"""

import argparse
import socket
import sys
import time
from datetime import datetime

HOST = "127.0.0.1"       # server address (localhost per the lab handout)
PORT = 5000              # agreed TCP port
MESSAGE = "Hello from client!"

# Task 3: wait at most 2 seconds for connect + response.
CLIENT_TIMEOUT_SECONDS = 2.0

# Task 4: bounded retries with exponential backoff.
MAX_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 0.5   # sleeps are 0.5 s, then 1 s (base * 2**(n-1))


def timestamp() -> str:
    """Current time as HH:MM:SS.mmm so logs show exactly when things happen."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def do_request() -> str:
    """One connection attempt: connect, send MESSAGE, return the reply.

    Raises OSError subclasses (ConnectionRefusedError, TimeoutError, etc.)
    which the caller handles via the retry loop.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(CLIENT_TIMEOUT_SECONDS)  # Task 3 requirement
        sock.connect((HOST, PORT))
        sock.sendall(MESSAGE.encode("utf-8"))
        data = sock.recv(1024)
        if not data:
            raise ConnectionError("server closed the connection without replying")
        return data.decode("utf-8")


def request_with_retry(max_attempts: int = MAX_ATTEMPTS) -> bool:
    """Task 4: try up to `max_attempts` times with exponential backoff.

    Backoff schedule: 0.5 s before attempt 2, 1 s before attempt 3.
    Returns True on success, False if all attempts fail.
    """
    for attempt in range(1, max_attempts + 1):
        print(f"[{timestamp()}] Attempt {attempt}/{max_attempts}: "
              f"sending \"{MESSAGE}\" to {HOST}:{PORT} ...")
        try:
            response = do_request()
            print(f"[{timestamp()}] Success: {response}")
            return True
        except ConnectionRefusedError:
            print(f"[{timestamp()}] Attempt {attempt} failed: "
                  f"connection refused (server is not listening).")
        except TimeoutError:
            print(f"[{timestamp()}] Attempt {attempt} failed: "
                  f"request timed out after {CLIENT_TIMEOUT_SECONDS}s.")
        except OSError as exc:
            print(f"[{timestamp()}] Attempt {attempt} failed: {exc}")

        if attempt < max_attempts:
            delay = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
            print(f"[{timestamp()}] Retrying in {delay:.1f}s...")
            time.sleep(delay)

    print(f"[{timestamp()}] Giving up after {max_attempts} attempts. "
          f"(Retry limits prevent infinite loops against a down service.)")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab 02 TCP client")
    parser.add_argument(
        "--no-retry", action="store_true",
        help="make a single attempt without retry/backoff (Tasks 1 & 3)",
    )
    args = parser.parse_args()

    if args.no_retry:
        try:
            response = do_request()
            print(f"[{timestamp()}] {response}")
        except TimeoutError:
            # Task 3 expected outcome: graceful handling, no crash traceback.
            print(f"[{timestamp()}] Request timed out. The server may be slow, "
                  f"but it has NOT necessarily crashed.")
            sys.exit(2)
        except OSError as exc:
            print(f"[{timestamp()}] Communication error: {exc}")
            sys.exit(1)
    else:
        ok = request_with_retry()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
