# Design Decisions

This document explains the architectural and implementation decisions made in this project.

The goal of the system was not only functionality, but deterministic behavior, scalability, and embedded robustness.

---

# 1. Interrupt Minimalism

## Decision
Interrupt Service Routines (ISR) perform only minimal work.

## Rationale

- ISRs must execute quickly to prevent latency accumulation.
- Blocking operations (USB transmission, GPIO logic, delays) are not performed inside interrupts.
- CAN RX ISR only reads hardware FIFO and pushes frames into a ring buffer.

## Result

- Predictable interrupt latency
- No nested interrupt starvation
- Deterministic execution behavior
- Easier reasoning about system timing

---

# 2. Single Producer / Single Consumer Ring Buffer

## Decision
NodeA uses a fixed-size ring buffer between CAN ISR (producer) and main loop (consumer).

## Rationale

- Avoids blocking in interrupt context
- Prevents data loss under burst load
- No dynamic memory allocation
- Lock-free due to SPSC design
- Head/tail indexes are atomic on Cortex-M (8-bit)

## Overflow Handling

If buffer is full:
- Frame is dropped
- Overflow counter increments
- Hardware FIFO is still drained

This prevents hardware overrun and preserves system stability.

## Result

- Deterministic memory usage
- Interrupt-safe communication
- Clear data flow separation

---

# 3. No Dynamic Memory Allocation

## Decision
No malloc/free used anywhere in firmware.

## Rationale

- Avoid heap fragmentation
- Avoid unpredictable allocation latency
- Eliminate allocation failure states
- Ensure static memory footprint

## Result

- Fully predictable memory usage
- Embedded-safe design
- Suitable for safety-critical adaptation

---

# 4. Hardware CAN Filtering

## Decision
NodeB uses hardware filter to accept only:

- Messages addressed to its node ID
- Broadcast messages

## Rationale

- Reduces CPU load
- Avoids unnecessary ISR executions
- Offloads filtering to CAN peripheral hardware

## Result

- Lower interrupt frequency
- Improved scalability for larger networks
- Deterministic CPU usage under bus load

---

# 5. Structured 11-bit Identifier

## Decision
CAN ID structured into:

Priority | Type | Source | Destination

## Rationale

- Clear routing model
- Logical message classification
- Hardware filtering by destination
- Arbitration control via priority bits

The ID encodes routing and arbitration, not application meaning.

## Result

- Scalable addressing
- Clean protocol layering
- Industry-aligned CAN usage

---

# 6. Payload-Driven Application Logic

## Decision
Application state is defined by payload, not identifier.

## Rationale

- Identifier classifies message
- Payload defines behavior
- Avoids encoding application semantics into ID
- Allows message reuse with different parameters

Example:
LED blink behavior is controlled via duration fields, not separate IDs.

## Result

- Extensible protocol
- Flexible command model
- Clean separation of concerns

---

# 7. Deterministic Timing Using Unsigned Arithmetic

## Decision
Timing comparisons use unsigned subtraction:


if ((current_time - last_event_time) >= interval)


## Rationale

- Safe across 32-bit wraparound
- No special overflow handling required
- Standard embedded timing pattern

## Result

- Robust long-running behavior
- No timing glitches after tick overflow

---

# 8. State Machine-Based Application Logic

## Decision
NodeB LED control implemented as explicit state machine:

- OFF
- ON
- BLINK

## Rationale

- Clear behavioral model
- Easy to extend
- No hidden state transitions
- Deterministic transitions

## Result

- Predictable application behavior
- Clean code readability
- Easy debugging and extension

---

# 9. Separation of Transport and Application Layers

## Decision
Clear separation between:

- Transport layer (CAN hardware)
- Protocol layer (ID structure)
- Application logic (LED control)
- Host tooling (Python CLI)

## Rationale

- Modular system design
- Replaceable components
- Testable layers
- Future scalability

## Result

- Clean architecture
- Clear responsibility boundaries
- Professional system design

---

# 10. Power-Aware Idle Strategy

## Decision
Main loop optionally uses `__WFI()` to sleep between interrupts.

## Rationale

- Reduces CPU usage
- Demonstrates low-power readiness
- Aligns with embedded best practices

## Considerations

- Must ensure no missed wake-up events
- Debugger interaction may affect behavior

## Result

- Efficient idle behavior
- Scalable for battery-based systems

---

# 11. Explicit Error Handling Strategy

## Decision

- Buffer overflow tracked via counter
- Invalid payload lengths ignored
- Invalid IDs filtered by hardware
- No silent memory corruption paths

## Rationale

Embedded systems must fail safely.

## Result

- Observable fault conditions
- Debug-friendly architecture
- Production-minded design

---

# 12. Scalability Philosophy

The system is intentionally structured so that adding:

- New message types
- Additional nodes
- Extended payload definitions
- Higher bus traffic

does not require architectural redesign.

Only protocol extension is needed.

---

# Summary

This project emphasizes:

- Deterministic embedded design
- Interrupt-safe architecture
- Structured CAN protocol usage
- Static memory safety
- Clear layering
- Scalability readiness

The focus was not only making it work, but making it robust and extensible.
