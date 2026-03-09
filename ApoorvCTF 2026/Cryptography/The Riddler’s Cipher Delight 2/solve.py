from Crypto.Util.number import long_to_bytes

N =  61335101030478919720870258161372353921031836932008941567053217346527987820466076329261287463549421023809770372764569882735210394312462119856344422486841273928867940096663293663837886684820260400512030980133100917131135731484950367326809489778133379519412767375186265844153579533926857758944406865260292926799
c =  22940309699977793906056877062420112639761767581900180883624329834487505119909951332117055492787889879690909162380572981397616990971145682582277715812733237198794876740691081318300157652208914119477544854893277826277566422100085011803508179920690747948460594038047416895021666000373415917463719352822333151422

def find_invpow(x, n):
    """Binary search to find the exact integer n-th root of x"""
    high = 1
    while high ** n < x:
        high *= 2
    low = high // 2
    while low < high:
        mid = (low + high) // 2
        if low < mid and mid**n < x:
            low = mid
        elif high > mid and mid**n > x:
            high = mid
        else:
            return mid
    return mid + 1

print("[*] Launching Cube Root Attack...")

# Test k wrap-arounds from 0 up to 100,000
for k in range(100000):
    target = c + (k * N)
    root = find_invpow(target, 3)
    
    if root**3 == target:
        print(f"[+] Success! The modulus wrapped {k} times.")
        flag = long_to_bytes(root)
        print("\n[+] FINAL FLAG:")
        print(flag.decode(errors='ignore'))
        break
    
    if k > 0 and k % 10000 == 0:
        print(f"[*] Still searching... checked {k} wrap-arounds.")
else:
    print("[-] Attack failed. The modulus wrapped too many times.")