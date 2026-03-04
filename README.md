# STM32 CAN Distributed Control System

This project implements a small distributed control system over CAN using STM32 microcontrollers.

## Architecture

- NodeA: USB ↔ CAN bridge
- NodeB: Application node controlling LED
- PC tool: Interactive CLI for control and diagnostics

## CAN ID Structure (11-bit)

Priority | Type | Source | Destination

- 2 bits Priority
- 3 bits Message Type
- 3 bits Source Node
- 3 bits Destination Node

## Message Types

- 000: Status
- 001: Control

## Control Payload Format

Byte 0 → Command  
Byte 1–2 → ON time (ms)  
Byte 3–4 → OFF time (ms)

## Status Payload Format

Byte 0 → LED Mode  
Byte 1–2 → ON time (ms)  
Byte 3–4 → OFF time (ms)

## Key Design Decisions

- ISR only updates state (no GPIO writes)
- Deterministic non-blocking timing in main loop
- Hardware CAN filtering by destination
- Unsigned wraparound-safe timing arithmetic
- PC-based protocol-aware CLI tool

## Example CLI
on
off
toggle
blink 1000 500

---

This project focuses on protocol design, embedded architecture, and deterministic real-time behavior rather than simple peripheral control.
