# Resonance Lock: The Harmonic Multiplier

| Field      | Value |
|------------|-------|
| Category   | Hardware |
| Points     | 304 |
| Solves     | 99 |

## Description

**Goal**  
Phase-lock UART baud-rate oscillator to **exactly 2,345,679 baud**, exercise the 512-bit hardware multiplier, extract the fixed flag token before the 45 s supercapacitor drains.

**Connection**  
`nc chals4.apoorvctf.xyz 1337`

**Protocol (8N1 framing)**

1. **Enter CALIBRATE**  
   Send single byte `0xCA` (no reply).

2. **Calibration burst** (repeat until LOCKED)  
   Send exactly **64× `0x55`** bytes with precise baud timing.  
   Server replies:  
   `ERR:+00123` / `ERR:-00045` (PPM error)  
   **Target:** |error| ≤ **1,000 PPM** for **5 consecutive** good bursts → `LOCKED`

3. **Locked mode** (45 s window)  
   Send: `0xAA` + **64-byte A** + **64-byte B** (512-bit big-endian operands)  
   Receive: `FLAG:apoorv{...}` (flag is fixed; any valid A/B works)

**Critical Warnings**  
- **HSM tamper fuse** is one-time and permanent per TCP session.  
  Never send: JTAG/SWD, flash reads, garbage bytes, or wrong patterns → `ERR:HSM_TAMPER_FUSE_BLOWN` (all future flags garbage).  
- Use **TCP_NODELAY**, send byte-by-byte.  
- Server times the **last 63 bytes** (first byte is trigger only).

**Solver tips**  
- Inter-byte delay = `10 / 2_345_679` s ≈ 4.263 µs.  
- Use busy-wait loop with `time.perf_counter_ns()` (sleep is too coarse).  
- No math needed — flag is constant once lock succeeds.

**Errors you’ll see**  
`ERR:PROTO`, `ERR:TIMEOUT`, `ERR:PATTERN`, `ERR:PAYLOAD`, `TIMEOUT:SUPERCAP_DRAINED`

Disconnect/reconnect for a fresh chip if fuse blows. Good luck!


> Author: b4bU-n@mBo0tHiR!

## Writeup

### Flag

```

```

### Executive Summary


### Vulnerability Analysis


### Exploit Strategy


### Implementation


### Execution & Results


