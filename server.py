import socket, threading, time, argparse
from datetime import datetime

HOST, PORT = "127.0.0.1", 5000
counter = 0
lock = threading.Lock()          # protects the shared counter

def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def current_delay(default):
    """Read delay (seconds) from delay.txt if it exists, so it can change without restarting."""
    try:
        with open("delay.txt") as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return default

def handle_client(conn, addr, delay):
    global counter
    with conn:
        data = conn.recv(1024).decode()
        with lock:
            counter += 1
            n = counter
        print(f"[{ts()}] Request #{n} START from {addr}: {data}")
        d = current_delay(delay)
        print(f"[{ts()}] Request #{n} using delay = {d}s")
        time.sleep(d)            # simulated processing delay
        conn.sendall(f"Server received: {data}".encode())
        print(f"[{ts()}] Request #{n} DONE  from {addr}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=2.0, help="seconds to delay each response")
    delay = ap.parse_args().delay
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT} (delay = {delay}s)")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr, delay), daemon=True).start()

if __name__ == "__main__":
    main()
