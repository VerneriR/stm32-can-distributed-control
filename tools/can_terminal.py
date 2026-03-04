import serial
import threading
import sys

# ---------------- Protocol Constants ----------------

TYPE_STATUS  = 0x00
TYPE_CONTROL = 0x01

CMD_LED_ON     = 0x01
CMD_LED_OFF    = 0x02
CMD_LED_TOGGLE = 0x03
CMD_LED_BLINK  = 0x04

LED_MODE_OFF   = 0
LED_MODE_ON    = 1
LED_MODE_BLINK = 2

SOURCE_PC   = 1
DEST_NODEB  = 2

# -----------------------------------------------------

def decode_id(std_id):
    priority = (std_id >> 9) & 0x03
    msg_type = (std_id >> 6) & 0x07
    source   = (std_id >> 3) & 0x07
    dest     = std_id & 0x07
    return priority, msg_type, source, dest


def build_id(priority, msg_type, source, dest):
    return (
        (priority << 9) |
        (msg_type << 6) |
        (source << 3) |
        dest
    )


# ---------------- Sending Functions ----------------

def send_frame(ser, std_id, data):
    frame = bytearray()
    frame.append(std_id & 0xFF)
    frame.append((std_id >> 8) & 0xFF)
    frame.append(len(data))
    frame.extend(data)
    ser.write(frame)


def send_on(ser):
    std_id = build_id(1, TYPE_CONTROL, SOURCE_PC, DEST_NODEB)
    send_frame(ser, std_id, [CMD_LED_ON])


def send_off(ser):
    std_id = build_id(1, TYPE_CONTROL, SOURCE_PC, DEST_NODEB)
    send_frame(ser, std_id, [CMD_LED_OFF])


def send_toggle(ser):
    std_id = build_id(1, TYPE_CONTROL, SOURCE_PC, DEST_NODEB)
    send_frame(ser, std_id, [CMD_LED_TOGGLE])


def send_blink(ser, on_ms, off_ms):
    std_id = build_id(1, TYPE_CONTROL, SOURCE_PC, DEST_NODEB)

    data = [
        CMD_LED_BLINK,
        (on_ms >> 8) & 0xFF,
        on_ms & 0xFF,
        (off_ms >> 8) & 0xFF,
        off_ms & 0xFF,
    ]

    send_frame(ser, std_id, data)


# ---------------- STATUS Decoder ----------------

def decode_status(data):
    if len(data) < 5:
        print("Invalid STATUS frame")
        return

    mode = data[0]
    on_time  = (data[1] << 8) | data[2]
    off_time = (data[3] << 8) | data[4]

    if mode == LED_MODE_OFF:
        mode_str = "OFF"
    elif mode == LED_MODE_ON:
        mode_str = "ON"
    elif mode == LED_MODE_BLINK:
        mode_str = "BLINK"
    else:
        mode_str = f"UNKNOWN({mode})"

    print(f"\n--- LED STATUS ---")
    print(f"Mode: {mode_str}")
    print(f"ON  time: {on_time} ms")
    print(f"OFF time: {off_time} ms")


# ---------------- Receiver Thread ----------------

def receiver(ser):
    buffer = bytearray()

    while True:
        byte = ser.read(1)
        if not byte:
            continue

        buffer += byte

        if len(buffer) >= 4:
            if buffer[0] != 0xAA:
                buffer.pop(0)
                continue

            std_id = buffer[1] | (buffer[2] << 8)
            dlc = buffer[3]

            if len(buffer) >= 4 + dlc:
                data = buffer[4:4+dlc]

                priority, msg_type, source, dest = decode_id(std_id)

                if msg_type == TYPE_STATUS:
                    decode_status(data)
                else:
                    print(f"\nRX ID=0x{std_id:03X} Data={data.hex()}")

                buffer = buffer[4+dlc:]


# ---------------- CLI Loop ----------------

def cli_loop(ser):
    print("\nCommands:")
    print("  on")
    print("  off")
    print("  toggle")
    print("  blink <on_ms> <off_ms>")
    print("  exit\n")

    while True:
        try:
            cmd = input("> ").strip()

            if cmd == "on":
                send_on(ser)

            elif cmd == "off":
                send_off(ser)

            elif cmd == "toggle":
                send_toggle(ser)

            elif cmd.startswith("blink"):
                parts = cmd.split()
                if len(parts) != 3:
                    print("Usage: blink <on_ms> <off_ms>")
                    continue

                on_ms = int(parts[1])
                off_ms = int(parts[2])
                send_blink(ser, on_ms, off_ms)

            elif cmd == "exit":
                sys.exit(0)

            else:
                print("Unknown command")

        except Exception as e:
            print("Error:", e)


# ---------------- Main ----------------

def main():
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)

    t = threading.Thread(target=receiver, args=(ser,), daemon=True)
    t.start()

    cli_loop(ser)


if __name__ == "__main__":
    main()
