# QBitFlipper

| Field      | Value |
|------------|-------|
| Category   | Hardware |
| Points     | 485 |
| Solves     | 29 |

## Description

While chasing The Spot through an abandoned Oscorp research facility, Miles Morales interrupted him while he was activating a strange prototype chip connected to the collider control systems.

Miles managed to shut the system down before it finished initializing, but The Spot escaped through a portal, leaving the device behind.

Spider-Byte recovered the hardware and began analyzing it.

The chip appears to be an experimental Oscorp System-on-Chip (SoC) composed of three custom modules:

* OSCORP QRYZEN™ Hybrid Core
* OSCORP QOREX™ 
* OSCORP QELIX™ Memory Array

1. **Components**

**OSCORP QRYZEN™ Hybrid Core**
A programmable processor responsible for coordinating system operations and interacting with the memory array.

**OSCORP QOREX™ **

.... Some IC it is not outputing any values.

**OSCORP QELIX™ Memory Array**
A 16-cell experimental storage array used by the processor.

Unfortunately, the QOREX ASIC is completely destroyed.

However, Spider-Byte discovered that the QRYZEN Hybrid Core still exposes a low-level debug interface.

Recovered Clues

From the lab we recovered:

    A diagnostic image dump from the device

    A diagram of the SoC architecture

Miles also noticed a note written on a nearby lab whiteboard:

Operator nibble mapping

0001 → BIT
0010 → PHASE
0011 → BITNPHASE

The processor expects correction instructions encoded as:

`[4-bit operator][4-bit address]`

Each instruction targets one of the 16 cells inside the QELIX memory array.

Each bits are addressed as
0,1,2,3
4,5,6,7
......
......,15

2. **Mission**

The processor is outputing decoding error find what is wrong and get an output.

nc chals4.apoorvctf.xyz 1338

> Author:  Eappen

## Files

- [code.png](./code.png)
- [Processor_Specifications.pdf](./Processor_Specifications.pdf)
- [Qbitflipper.jpg](./Qbitflipper.jpg)

## Writeup

### Flag

```

```

### Executive Summary


### Vulnerability Analysis


### Exploit Strategy


### Implementation


### Execution & Results


