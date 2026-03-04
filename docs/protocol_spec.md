# CAN Protocol Specification

## Overview

This document defines the custom CAN-based communication protocol used in the STM32 CAN Distributed Control System.

The protocol uses:

- Standard 11-bit CAN identifiers
- Data frames only (no RTR)
- Up to 8-byte payload (CAN 2.0A)
- Deterministic message classification via structured ID fields

The protocol separates message routing (ID) from application data (payload).

---

# 1. CAN Frame Format

Each CAN frame consists of:

- 11-bit Identifier
- DLC (0–8 bytes)
- Data Payload (0–8 bytes)

This system does not use extended (29-bit) identifiers.

---

# 2. 11-bit Identifier Structure

The 11-bit identifier is structured as follows:

| Bits  | Field        | Size | Description |
|--------|-------------|------|-------------|
| 10–9  | Priority     | 2    | Message arbitration priority |
| 8–6   | Message Type | 3    | Defines logical message category |
| 5–3   | Source Node  | 3    | Sender node ID |
| 2–0   | Destination  | 3    | Target node ID |

Total: 11 bits

---

## 2.1 Bit Layout Diagram


[10 9] [8 7 6] [5 4 3] [2 1 0]
Priority Type Source Destination


---

## 2.2 Node IDs

| Node | ID (3-bit) |
|------|------------|
| NodeA (USB Bridge) | 001 |
| NodeB (LED Device) | 010 |
| Broadcast          | 111 |

---

## 2.3 Message Types

| Type | Binary | Description |
|------|--------|------------|
| 000  | Status | Periodic or state reporting |
| 001  | Control | Device control command |
| 010–111 | Reserved | Future extension |

---

# 3. Arbitration Priority

Lower numeric identifier = higher arbitration priority.

Priority field (2 bits):

| Value | Meaning |
|--------|---------|
| 00 | Highest priority |
| 01 | Medium |
| 10 | Low |
| 11 | Lowest |

This allows deterministic bus behavior under load.

---

# 4. Control Message Specification

Message Type = `001`

Used to command application behavior.

## 4.1 Payload Structure

| Byte | Field |
|------|-------|
| 0    | Command |
| 1–2  | ON duration (ms, uint16, little-endian) |
| 3–4  | OFF duration (ms, uint16, little-endian) |
| 5–7  | Reserved |

Maximum DLC: 5 bytes

---

## 4.2 Command Codes

| Value | Meaning |
|--------|---------|
| 0x00 | LED OFF |
| 0x01 | LED ON |
| 0x02 | LED TOGGLE |
| 0x03 | LED BLINK |

For BLINK command:

- ON duration defines active time
- OFF duration defines inactive time

---

# 5. Status Message Specification

Message Type = `000`

Used by NodeB to report LED state.

## 5.1 Payload Structure

| Byte | Field |
|------|-------|
| 0    | Current Mode |
| 1–2  | ON duration (ms) |
| 3–4  | OFF duration (ms) |
| 5–7  | Reserved |

Maximum DLC: 5 bytes

---

## 5.2 Mode Values

| Value | Meaning |
|--------|---------|
| 0x00 | OFF |
| 0x01 | ON |
| 0x02 | BLINK |

---

# 6. Broadcast Behavior

Destination `111` indicates broadcast.

- Any node may process broadcast control messages
- Status messages are not broadcast in this implementation

Hardware filtering may be configured to accept:
- Specific node ID
- Broadcast
- Both

---

# 7. Encoding Example

Example:

Control command from NodeA (001) to NodeB (010), blink 1000 ms ON / 500 ms OFF.

Fields:

- Priority = 01
- Type = 001 (Control)
- Source = 001
- Destination = 010

Binary ID:


01 001 001 010


Payload:


Byte 0: 0x03
Byte 1–2: 0xE8 0x03 (1000 ms)
Byte 3–4: 0xF4 0x01 (500 ms)


---

# 8. Determinism and Constraints

- Maximum payload: 8 bytes
- No multi-frame transport implemented
- All timing values use unsigned arithmetic
- No dynamic memory allocation
- Messages exceeding 8 bytes must be split across frames (future extension)

---

# 9. Scalability Considerations

The protocol allows:

- Up to 8 nodes (3-bit addressing)
- Up to 8 logical message types
- Priority-based arbitration
- Broadcast capability
- Future payload expansion

The architecture allows migration to:

- Extended 29-bit identifiers
- Multi-frame transport layer
- Diagnostic message classes

without redesigning the ID structure concept.

---

# 10. Design Philosophy

The protocol intentionally:

- Uses ID for routing and classification
- Uses payload for application data
- Avoids encoding application meaning into ID
- Separates transport from logic
- Enables hardware filtering by destination

This ensures clean layering and system scalability.
