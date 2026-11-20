import socket, time, argparse
from datetime import datetime

HOST, PORT = "127.0.0.1", 5000
BACKOFF = [0.5, 1]               # wait before attempt 2 and attempt 3

def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def send_once(message, timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((HOST, PORT))
        s.sendall(message.encode())
        return s.recv(1024).decode()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=4.0, help="client socket timeout (s)")
    ap.add_argument("--attempts", type=int, default=3, help="max attempts (1 = no retry)")
    ap.add_argument("--message", default="Hello from client!")
    a = ap.parse_args()
    attempts = min(a.attempts, 3)   # never more than 3 tries
    for i in range(1, attempts + 1):
        try:
            print(f"[{ts()}] Attempt {i}: sending '{a.message}' (timeout {a.timeout}s)")
            print(f"[{ts()}] Client:", send_once(a.message, a.timeout))
            return
        except socket.timeout:
            print(f"[{ts()}] Attempt {i} failed: request timed out")
        except ConnectionRefusedError:
            print(f"[{ts()}] Attempt {i} failed: connection refused")
        except OSError as e:
            print(f"[{ts()}] Attempt {i} failed: {e}")
        if i < attempts:
            wait = BACKOFF[i - 1]
            print(f"[{ts()}] Waiting {wait}s before retry...")
            time.sleep(wait)
    print(f"[{ts()}] All {attempts} attempt(s) failed. Giving up.")

if __name__ == "__main__":
    main()
