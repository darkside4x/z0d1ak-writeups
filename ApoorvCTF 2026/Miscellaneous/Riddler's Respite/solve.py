import re
import socket

# Configuration
TARGET_HOST = "chals1.apoorvctf.xyz"
TARGET_PORT = 13001

# Regex patterns for cleanup and extraction
CLEAN_ANSI = re.compile(rb"\x1b\[[0-9;]*m")
EXTRACT_FLAG = re.compile(rb"apoorvctf\{[^}]+\}")

def fetch_data(conn: socket.socket, max_wait: float = 1.4) -> bytes:
    """Reads from the socket until the timeout is reached."""
    conn.settimeout(max_wait)
    buffer = b""
    while True:
        try:
            data_chunk = conn.recv(4096)
            if not data_chunk:
                break
            buffer += data_chunk
        except socket.timeout:
            break
        except Exception:
            break
    return buffer

def execute_phase(pass_key: str, menu_opt: str, payloads: list[str]) -> list[str]:
    """Connects, authenticates, drops payloads, and extracts tokens."""
    raw_bytes = b""
    conn = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=6)

    # Initial connection and auth
    raw_bytes += fetch_data(conn, 1.0)
    conn.sendall(f"{pass_key}\n".encode())
    raw_bytes += fetch_data(conn, 2.0)

    # Menu selection
    conn.sendall(f"{menu_opt}\n".encode())
    raw_bytes += fetch_data(conn, 1.8)

    # Inform server of payload count
    conn.sendall(f"{len(payloads)}\n".encode())
    raw_bytes += fetch_data(conn, 1.2)

    # Send payloads
    for payload in payloads:
        conn.sendall(f"{payload}\n".encode())
        raw_bytes += fetch_data(conn, 1.5)

    # Final read and cleanup
    raw_bytes += fetch_data(conn, 2.2)
    conn.close()

    # Extract all flags/tokens from the response
    extracted_flags = [
        match.group(0).decode(errors="ignore") 
        for match in EXTRACT_FLAG.finditer(raw_bytes)
    ]
    return extracted_flags

def generate_permutation(length: int) -> str:
    """Generates a cyclic shift of an array to maximize cycle length."""
    shifted = list(range(2, length + 1)) + [1]
    return f"{length} " + " ".join(str(num) for num in shifted)

def main():
    # Phase 1: MEX/XOR Bypasses
    phase_1_payloads = [
        "2 1 1",
        "2 0 20",
        "2 0 69",
        "2 0 12345",
        "12 0 1 2 3 4 5 6 7 8 9 10 65535",
    ]

    # Phase 2: Wiener Index Tree Edges
    phase_2_payloads = [
        "3 1 2 2 3",
        "6 4 1 5 1 1 2 2 3 3 6",
        "8 1 2 1 3 1 4 1 5 1 6 1 7 1 8",
        "11 2 8 3 7 4 8 5 7 6 7 8 1 1 7 10 7 7 9 9 11",
        "18 2 6 7 3 8 5 5 4 9 14 11 14 12 4 13 4 14 6 6 3 15 10 10 4 4 3 16 3 17 3 3 1 1 18",
    ]

    # Phase 3: Permutation Cycles
    phase_3_targets = [3, 8, 15, 19, 67]
    phase_3_payloads = [generate_permutation(target) for target in phase_3_targets]

    # Execution Flow
    print("[*] Initiating Phase 1 Bypass...")
    flags_1 = execute_phase("x", "1", phase_1_payloads)
    if not flags_1:
        raise SystemExit("[-] Phase 1 failed: No token retrieved.")
    key_1 = flags_1[-1]
    print(f"[+] Acquired Key 1: {key_1}")

    print("\n[*] Initiating Phase 2 Bypass...")
    flags_2 = execute_phase(key_1, "2", phase_2_payloads)
    if not flags_2:
        raise SystemExit("[-] Phase 2 failed: No token retrieved.")
    key_2 = flags_2[-1]
    print(f"[+] Acquired Key 2: {key_2}")

    print("\n[*] Initiating Phase 3 Bypass...")
    flags_3 = execute_phase(key_2, "3", phase_3_payloads)
    if not flags_3:
        raise SystemExit("[-] Phase 3 failed: Final flag not retrieved.")
    final_flag = flags_3[-1]
    print(f"\n[!] CAPTURED FINAL FLAG: {final_flag}")

if __name__ == "__main__":
    main()