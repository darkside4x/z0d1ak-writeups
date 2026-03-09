import json
import socket

HOST = "chals2.apoorvctf.xyz"
PORT = 13337

class NoisyOracle:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        self.f = self.s.makefile('rw', buffering=1)
        self.f.readline() 
        self.query_count = 0

    def query(self, option, **kwargs):
        self.query_count += 1
        payload = json.dumps({"option": option, **kwargs})
        self.f.write(payload + '\n')
        
        resp = self.f.readline().strip()
        if not resp:
            raise ValueError(f"Empty response on query {self.query_count}. Dropped?")
        
        return json.loads(resp)

    def get_ct(self):
        res = self.query("encrypt")
        return bytes.fromhex(res["ct"])

def solve():
    oracle = NoisyOracle()
    
    print("[*] Calibrating noise levels...")
    hits = 0
    rounds = 300 
    for _ in range(rounds):
        res = oracle.query("unpad", ct="ff"*32)
        if res.get("result") == True:
            hits += 1
    
    p_true_invalid = hits / rounds
    p_true_valid = 1.0 - p_true_invalid 
    print(f"[*] Calibration Complete: P(True|Invalid) ≈ {p_true_invalid:.3f}")

    full_ct = oracle.get_ct()
    iv = full_ct[:16]
    blocks = [full_ct[16:32], full_ct[32:48]]
    
    recovered_secret = ""
    hex_chars = "0123456789abcdef"

    for b_idx, ct_block in enumerate(blocks):
        prev_block = iv if b_idx == 0 else blocks[b_idx-1]
        decoded_block = [0] * 16

        for i in range(15, -1, -1):
            pad_val = 16 - i
            posteriors = {c: 1.0/16.0 for c in hex_chars}
            
            # 99.9% confidence required to survive the 32-byte string probability
            while max(posteriors.values()) < 0.999:
                # Maximize expected info gain by testing candidate closest to 50%
                char_to_test = min(hex_chars, key=lambda c: abs(posteriors[c] - 0.5))

                test_iv = bytearray(16)
                for j in range(i + 1, 16):
                    test_iv[j] = decoded_block[j] ^ prev_block[j] ^ pad_val
                
                test_iv[i] = ord(char_to_test) ^ prev_block[i] ^ pad_val
                
                res = oracle.query("unpad", ct=(test_iv + ct_block).hex())
                obs = res.get("result")

                if obs == True:
                    l_valid = p_true_valid
                    l_invalid = p_true_invalid
                else:
                    l_valid = 1.0 - p_true_valid
                    l_invalid = 1.0 - p_true_invalid

                # Bayesian Update
                for c in hex_chars:
                    if c == char_to_test:
                        posteriors[c] *= l_valid
                    else:
                        posteriors[c] *= l_invalid

                # Normalize
                norm_factor = sum(posteriors.values())
                for c in hex_chars: 
                    posteriors[c] /= norm_factor
                
            best_char = max(posteriors, key=posteriors.get)
            decoded_block[i] = ord(best_char)
            print(f"[+] Found Block {b_idx}, Byte {i:02d}: '{best_char}' (Conf: {posteriors[best_char]:.4f}) | Total Queries: {oracle.query_count}")
        
        recovered_secret += "".join(chr(x) for x in decoded_block)

    print(f"\n[*] Full Recovered Secret: {recovered_secret}")
    print(f"[*] Total Queries Used: {oracle.query_count} / 10000")
    
    final_res = oracle.query("check", message=recovered_secret)
    print(f"[*] Server Response: {final_res}")

if __name__ == "__main__":
    solve()