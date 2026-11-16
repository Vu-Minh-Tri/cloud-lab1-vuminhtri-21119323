"""Lab 02 — Distributed Client-Server Application (TCP server).

Tasks covered:
  Task 1: Bind to 127.0.0.1:5000, accept a connection, receive the client
          message, print the client address + message, and echo a reply.
  Task 2: Handle multiple clients concurrently with one thread per client,
          including a simulated 2-second processing delay.
  Task 3: Simulate a slow response (SERVER_DELAY_SECONDS env var) so clients
          can experience timeouts while the server keeps running.

Usage:
    python server.py                       # normal mode (2s processing delay)
    SERVER_DELAY_SECONDS=5 python server.py   # slow-response test for Task 3

Standard library only; runs on localhost — no cloud account required.
"""

import os
import socket
import sys
import threading
import time
from datetime import datetime

HOST = "127.0.0.1"  # loopback interface (localhost)
PORT = 5000         # agreed TCP port from the lab handout


def timestamp() -> str:
    """Current time as HH:MM:SS.mmm for overlap evidence in the server log."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def handle_client(conn: socket.socket, addr: tuple, delay: float) -> None:
    """Serve one connected client on its own thread (Task 2 concurrency)."""
    print(f"[{timestamp()}] Connection accepted from {addr}")
    try:
        # Receive up to 1024 bytes of the client's request.
        data = conn.recv(1024)
        if not data:
            print(f"[{timestamp()}] {addr} closed the connection before sending data.")
            return

        message = data.decode("utf-8")
        # Task 1 requirement: print the client address and received message.
        print(f"[{timestamp()}] Received from {addr}: {message}")

        # Task 2/3: simulated processing delay.
        print(f"[{timestamp()}] Processing request from {addr} "
              f"(delaying {delay:.1f}s)...")
        time.sleep(delay)

        # Echo an acknowledgement back to the client.
        response = f"Server received: {message}"
        conn.sendall(response.encode("utf-8"))
        print(f"[{timestamp()}] Replied to {addr}: {response}")
    except ConnectionResetError:
        print(f"[{timestamp()}] {addr} reset the connection (client may have timed out).")
    finally:
        conn.close()
        print(f"[{timestamp()}] Connection with {addr} closed.")


def main() -> None:
    # Task 3 knob: how long the server waits before replying.
    # Default is the 2-second simulated processing delay from Task 2.
    # Use --delay 5 (or SERVER_DELAY_SECONDS=5) to demonstrate timeouts.
    delay = float(os.environ.get("SERVER_DELAY_SECONDS", "2"))
    if len(sys.argv) > 2 and sys.argv[1] == "--delay":
        delay = float(sys.argv[2])

    # SOCK_STREAM => TCP; backlog allows the OS to queue incoming connections
    # while we are busy accepting/handling others.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        # SO_REUSEADDR lets us restart the server quickly during experiments
        # without waiting for TIME_WAIT to expire on port 5000.
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen()
        print(f"[{timestamp()}] Server listening on {HOST}:{PORT} "
              f"(response delay: {delay:.1f}s)")

        try:
            while True:
                conn, addr = server_sock.accept()
                # Task 2: each client gets its own daemon thread, so new
                # connections are accepted immediately while old ones process.
                worker = threading.Thread(
                    target=handle_client, args=(conn, addr, delay), daemon=True
                )
                worker.start()
                print(f"[{timestamp()}] Active client threads: "
                      f"{threading.active_count() - 1}")
        except KeyboardInterrupt:
            print(f"\n[{timestamp()}] Server shutting down (Ctrl+C).")


if __name__ == "__main__":
    main()
