from PIL import Image

def solve():
    # Load image and access pixel map
    img = Image.open("chall4.png").convert("RGB")
    pixels = img.load()
    width, height = img.size

    bits = []
    
    # Iterate through pixels to extract the cycled bits
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # The "Cycle": Red bit 0 -> Green bit 1 -> Blue bit 2
            bits.append((r >> 0) & 1)
            bits.append((g >> 1) & 1)
            bits.append((b >> 2) & 1)

    # Reconstruct bits into bytes
    extracted_data = bytearray()
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) < 8: break
        
        # Binary to Integer conversion
        byte_val = 0
        for bit in byte_bits:
            byte_val = (byte_val << 1) | bit
        extracted_data.append(byte_val)

    # Search for flag format
    final_string = extracted_data.decode('ascii', errors='ignore')
    if "apoorvctf" in final_string:
        print(f"[+] Flag Found: {final_string[final_string.find('apoorvctf'):final_string.find('}')+1]}")

if __name__ == "__main__":
    solve()