import argparse
import itertools
import re
import socket
import time
from typing import List, Sequence, Tuple

try:
    from wordfreq import zipf_frequency
except Exception:
    zipf_frequency = None

HOST = "chals2.apoorvctf.xyz"
PORT = 13420

LEET = {
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "9": "g",
}


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def recv_until(sock: socket.socket, markers: Sequence[bytes], timeout: float = 6.0) -> str:
    sock.settimeout(0.2)
    out = b""
    end = time.time() + timeout
    while time.time() < end:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            out += chunk
            if any(marker in out for marker in markers):
                break
        except Exception:
            pass
    return strip_ansi(out.decode(errors="replace"))


def send_line(sock: socket.socket, line: str, expect: bytes = b">>", timeout: float = 6.0) -> str:
    sock.sendall((line + "\n").encode())
    return recv_until(sock, [expect], timeout)


def add_entry(sock: socket.socket, site: str, password: str) -> None:
    send_line(sock, "add", expect=b"site>", timeout=3)
    send_line(sock, site, expect=b"password>", timeout=3)
    send_line(sock, password, expect=b">>", timeout=4)


def parse_list_output(text: str) -> List[Tuple[int, str, str]]:
    if "Index | Site" not in text:
        return []

    body = text.split("Index | Site", 1)[1]
    body = body.split("\n\n===", 1)[0]
    matches = list(re.finditer(r"(^|\n)\s*(\d+)\s*\|", body))

    rows: List[Tuple[int, str, str]] = []
    for i, match in enumerate(matches):
        start = match.start(2)
        end = matches[i + 1].start(2) if i + 1 < len(matches) else len(body)
        chunk = body[start:end]
        parts = chunk.split("|", 2)
        if len(parts) < 3:
            continue

        idx_raw = parts[0].strip()
        if not idx_raw.isdigit():
            continue

        site = parts[1].strip()
        cipher = "".join(ch for ch in parts[2].lower() if ch in "0123456789abcdef.;")
        if cipher:
            rows.append((int(idx_raw), site, cipher))

    return rows


def poly_eval(coeff: List[int], x: int) -> int:
    value = 0
    for c in coeff:
        value = value * x + c
    return value


def poly_div(coeff: List[int], root: int) -> List[int]:
    out = [coeff[0]]
    for c in coeff[1:-1]:
        out.append(out[-1] * root + c)
    return out


def roots_from_block(block: str) -> List[int]:
    e1, e2, e3, e4 = [int(x, 16) for x in block.split(".")]
    coeff = [1, -e1, e2, -e3, e4]
    roots: List[int] = []

    for candidate in range(256):
        while len(coeff) > 1 and poly_eval(coeff, candidate) == 0:
            roots.append(candidate)
            coeff = poly_div(coeff, candidate)

    if len(roots) != 4:
        raise RuntimeError(f"failed root recovery for block {block}: {roots}")
    return roots


def decode_blocks_with_key(ciphertext: str, key: int) -> List[List[int]]:
    blocks = ciphertext.split(";")
    decoded: List[List[int]] = []

    for i, block in enumerate(blocks):
        ys = roots_from_block(block)
        plain = [y ^ key for y in ys]
        if i == len(blocks) - 1:
            plain = [x for x in plain if x != 0]
        decoded.append(plain)

    return decoded


def recover_session_key(rows: List[Tuple[int, str, str]]) -> int:
    probe = next(row for row in rows if row[1] == "probe.local")
    e1_hex = probe[2].split(";")[0].split(".")[0]
    e1 = int(e1_hex, 16)
    return (e1 // 4) ^ ord("A")


def verify_permutation_invariance(rows: List[Tuple[int, str, str]]) -> bool:
    probe_names = {
        "abcd.local",
        "abdc.local",
        "acbd.local",
        "bacd.local",
        "dcba.local",
    }
    ciphers = [cipher for _, site, cipher in rows if site in probe_names]
    return len(ciphers) == 5 and len(set(ciphers)) == 1


def norm_leet(token: str) -> str:
    return "".join(LEET.get(ch, ch) for ch in token.lower())


def token_score(token: str) -> float:
    if not token:
        return 0.0

    norm = norm_leet(token)
    score = 0.0

    if zipf_frequency is not None:
        z = zipf_frequency(norm, "en")
        score += z if z > 0 else -3.0
    else:
        score += 0.2 * len(norm)

    if len(norm) == 1:
        score -= 1.5

    bonus_words = {
        "flag",
        "crypto",
        "crypt",
        "read",
        "this",
        "you",
        "broke",
        "never",
        "gonna",
        "give",
        "great",
        "work",
        "polynomial",
        "gods",
        "cake",
        "lie",
        "both",
        "real",
        "fake",
        "kant",
        "moral",
        "math",
        "think",
        "therefore",
        "pwn",
    }
    if norm in bonus_words:
        score += 1.5

    return score


def beam_decode(block_sets: List[List[int]], width: int = 2000, keep: int = 8) -> List[Tuple[float, str]]:
    perms_by_block: List[List[str]] = []
    for block in block_sets:
        chars = [chr(x) for x in block]
        perms = sorted(set("".join(p) for p in itertools.permutations(chars)))
        perms_by_block.append(perms)

    if "apoo" not in perms_by_block[0] or "rvct" not in perms_by_block[1]:
        return []

    perms_by_block[0] = ["apoo"]
    perms_by_block[1] = ["rvct"]
    perms_by_block[2] = [p for p in perms_by_block[2] if p.startswith("f{")]
    perms_by_block[-1] = [p for p in perms_by_block[-1] if p.endswith("}")]

    if not perms_by_block[2] or not perms_by_block[-1]:
        return []

    # (score, text, current_token, in_flag, closed)
    beam: List[Tuple[float, str, str, bool, bool]] = [(0.0, "", "", False, False)]

    for block_i, choices in enumerate(perms_by_block):
        candidates: List[Tuple[float, str, str, bool, bool]] = []
        for score, text, token, in_flag, closed in beam:
            if closed:
                continue
            for frag in choices:
                ns, nt, ntok, nif, ncl = score, text, token, in_flag, closed
                bad = False
                for ch in frag:
                    nt += ch
                    if not nif:
                        if ch == "{":
                            nif = True
                            ntok = ""
                        elif ch == "}":
                            bad = True
                            break
                        continue

                    if ch == "}":
                        ns += token_score(ntok)
                        ntok = ""
                        ncl = True
                    elif ch == "_":
                        ns += token_score(ntok)
                        ntok = ""
                    elif ch.isalnum():
                        ntok += ch
                    else:
                        bad = True
                        break

                if bad:
                    continue

                if block_i == len(perms_by_block) - 1 and not ncl:
                    ns -= 8.0

                candidates.append((ns, nt, ntok, nif, ncl))

        if not candidates:
            return []

        candidates.sort(key=lambda x: x[0], reverse=True)
        beam = candidates[:width]

    ranked: List[Tuple[float, str]] = []
    best_by_text = {}

    for score, text, token, in_flag, closed in beam:
        final_score = score + token_score(token)
        if in_flag and closed and text.startswith("apoorvctf{") and text.endswith("}"):
            prev = best_by_text.get(text)
            if prev is None or final_score > prev:
                best_by_text[text] = final_score

    for text, score in best_by_text.items():
        ranked.append((score, text))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked[:keep]


def collect_rows() -> Tuple[List[Tuple[int, str, str]], int, bool]:
    sock = socket.create_connection((HOST, PORT))
    try:
        recv_until(sock, [b">>"], timeout=4)

        add_entry(sock, "probe.local", "AAAA")
        add_entry(sock, "abcd.local", "ABCD")
        add_entry(sock, "abdc.local", "ABDC")
        add_entry(sock, "acbd.local", "ACBD")
        add_entry(sock, "bacd.local", "BACD")
        add_entry(sock, "dcba.local", "DCBA")

        rows = parse_list_output(send_line(sock, "list", expect=b">>", timeout=10))
        key = recover_session_key(rows)
        perm_ok = verify_permutation_invariance(rows)

        send_line(sock, "quit", expect=b"Goodbye.", timeout=2)
        return rows, key, perm_ok
    finally:
        try:
            sock.close()
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batvault evidence-based solver (no hardcoded final flag)."
    )
    parser.add_argument("--verbose", action="store_true", help="Show technical metadata.")
    parser.add_argument(
        "--top-per-entry",
        type=int,
        default=5,
        help="How many candidates to print per entry (default: 5).",
    )
    parser.add_argument(
        "--best-only",
        action="store_true",
        help="Print only the highest-scoring candidate across all entries.",
    )
    args = parser.parse_args()

    rows, key, perm_ok = collect_rows()

    if args.verbose:
        print(f"[+] session key: {key}")
        print(f"[+] permutation invariant: {perm_ok}")
        print(f"[+] parsed rows: {len(rows)}")
        if zipf_frequency is None:
            print("[!] wordfreq missing, using fallback scoring")

    all_ranked: List[Tuple[float, int, str, str]] = []
    by_entry: List[Tuple[int, str, List[Tuple[float, str]]]] = []

    for idx, site, cipher in rows:
        if site.endswith(".local"):
            continue

        block_sets = decode_blocks_with_key(cipher, key)
        ranked = beam_decode(block_sets, keep=max(1, args.top_per_entry))
        by_entry.append((idx, site, ranked))

        for score, text in ranked:
            all_ranked.append((score, idx, site, text))

    all_ranked.sort(key=lambda x: x[0], reverse=True)

    if args.best_only:
        if all_ranked:
            print(all_ranked[0][3])
        else:
            print("no candidate")
        return

    for idx, site, ranked in by_entry:
        print(f"\n[{idx}] {site}")
        if not ranked:
            print("  no ranked candidates")
            continue
        for score, text in ranked:
            print(f"  {score:7.2f}  {text}")

    if all_ranked:
        top = all_ranked[0]
        print("\n== Best Overall Candidate ==")
        print(f"score={top[0]:.2f}, index={top[1]}, site={top[2]}")
        print(top[3])


if __name__ == "__main__":
    main()
