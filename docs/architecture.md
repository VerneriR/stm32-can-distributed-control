# System Architecture

## Overview

This project implements a small distributed embedded control system over CAN using STM32 microcontrollers.

The system consists of:

- **NodeA** – USB ↔ CAN bridge (interface node)
- **NodeB** – Application node controlling LED behavior
- **PC Tool** – Python-based CLI for control and diagnostics

The architecture separates transport, protocol, and application logic to ensure deterministic behavior and scalability.

---

## High-Level Architecture

PC Tool  <----USB CDC---->  NodeA  <----CAN Bus---->  NodeB

- The PC tool sends control commands over USB.
- NodeA translates USB payloads into CAN frames.
- NodeB processes CAN frames according to protocol rules.
- NodeB periodically transmits status frames.
- NodeA forwards status frames back to the PC.

---

## Node Responsibilities

### NodeA – USB-CAN Bridge

**Role:** Transport and protocol interface.

Responsibilities:

- Receive CAN frames via interrupt
- Push frames into a lock-free ring buffer (ISR context)
- Process queue in main loop
- Forward frames to USB CDC interface
- Convert USB commands into CAN frames
- Maintain deterministic non-blocking behavior

Design Characteristics:

- ISR kept minimal (no GPIO operations)
- Single Producer / Single Consumer ring buffer
- Hardware CAN filtering enabled
- USB transmission handled outside interrupt context
- Optional low-power idle using `__WFI()`

---

### NodeB – Application Node

**Role:** Device-level application logic.

Responsibilities:

- Hardware filter for destination ID
- Process control messages
- Manage LED state machine (OFF / ON / BLINK)
- Periodically transmit LED status frames

Design Characteristics:

- No dynamic memory allocation
- Deterministic timing using system tick
- Application logic separated from interrupt context
- Minimal ISR workload

---

## Interrupt and Data Flow

### CAN Receive Flow (NodeA)

1. CAN RX interrupt fires
2. ISR reads hardware FIFO
3. Frame pushed into software ring buffer
4. Main loop checks buffer
5. Frame formatted for USB transmission
6. USB transmit initiated

This ensures:

- No blocking inside ISR
- No USB operations inside interrupt context
- Deterministic queue processing

---

## Ring Buffer Architecture

NodeA uses a fixed-size ring buffer:

- Single producer (CAN ISR)
- Single consumer (main loop)
- Head/tail index model
- Overflow counter for diagnostics

This guarantees:

- Lock-free operation
- Predictable memory usage
- ISR-safe communication
- No race conditions (SPSC model)

---

## Timing Model

NodeB LED control operates as a state machine:

- ON
- OFF
- BLINK (configurable on/off durations)

Blink timing uses unsigned time arithmetic:


if ((current_time - last_toggle_time) >= interval)


This ensures correct behavior even across 32-bit tick wraparound.

---

## Protocol Separation

The system separates:

- Transport layer (CAN)
- Framing layer (11-bit structured ID)
- Application payload
- Host tooling

This enables:

- Scalability to additional nodes
- Future extension of message types
- Clear responsibility boundaries
- Deterministic embedded behavior

---

## Determinism and Robustness Principles

The design intentionally avoids:

- Blocking delays
- Dynamic memory allocation
- Complex logic in interrupt context
- Direct hardware manipulation inside ISR

Instead, it emphasizes:

- Interrupt minimalism
- Queue-based communication
- Explicit state machines
- Hardware filtering
- Protocol-driven behavior

---

## Scalability Considerations

The architecture can scale to:

- Multiple application nodes
- Additional message types
- More complex payload definitions
- Higher bus load scenarios

Only protocol extension is required — not architectural redesign.

---

## Summary

This system demonstrates:

- Embedded interrupt-safe design
- Deterministic main-loop processing
- Custom CAN protocol implementation
- Hardware-assisted filtering
- Host-tool integration
- Separation of transport and application logic
