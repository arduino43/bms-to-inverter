import struct
import time
import can

# Utility to set/clear a bit

def set_bit(value: int, index: int, on: bool) -> int:
    if on:
        value |= 1 << index
    else:
        value &= ~(1 << index)
    return value

# Preset battery pack data similar to SimulatedBatteryPackPlugin
PACK_SOC = 500                 # 0.1%% -> 50%%
PACK_SOH = 990                 # 0.1%% -> 99%%
PACK_CURRENT = 0               # 0.1A
PACK_VOLTAGE = 520             # 0.1V -> 52V
MAX_CHARGE_CURRENT = 200       # 0.1A
MAX_DISCHARGE_CURRENT = 200    # 0.1A
MAX_VOLTAGE_LIMIT = 540        # 0.1V
MIN_VOLTAGE_LIMIT = 480        # 0.1V
TEMP_AVERAGE = 250             # 0.1C -> 25C

MANUFACTURER = "PN"            # example manufacturer string


def create_frames():
    frames = []

    # 0x351 Charge/Discharge limits
    data_351 = struct.pack('<HhhH', MAX_VOLTAGE_LIMIT, MAX_CHARGE_CURRENT,
                           MAX_DISCHARGE_CURRENT, MIN_VOLTAGE_LIMIT)
    frames.append((0x351, data_351))

    # 0x355 SOC/SOH
    data_355 = struct.pack('<HH', PACK_SOC // 10, PACK_SOH // 10)
    frames.append((0x355, data_355))

    # 0x356 Pack voltage, current, temperature
    data_356 = struct.pack('<hhh', PACK_VOLTAGE * 10, PACK_CURRENT, TEMP_AVERAGE)
    frames.append((0x356, data_356))

    # 0x35C Charge/Discharge flags
    flags = 0
    flags = set_bit(flags, 3, False)  # request full charge
    flags = set_bit(flags, 4, False)  # force charge
    flags = set_bit(flags, 5, False)  # force charge
    flags = set_bit(flags, 6, False)  # discharge MOS state
    flags = set_bit(flags, 7, False)  # charge MOS state
    data_35c = struct.pack('<B', flags) + b"\x00" * 7
    frames.append((0x35C, data_35c))

    # 0x35E Manufacturer
    manu_bytes = MANUFACTURER.encode('ascii')[:8]
    data_35e = manu_bytes + b"\x00" * (8 - len(manu_bytes))
    frames.append((0x35E, data_35e))

    # 0x359 Alarms (no alarms)
    alarm_bits = 0
    data_359 = struct.pack('<IBBB', alarm_bits, 0, 0x50, 0x4E)
    frames.append((0x359, data_359))

    return frames


def main():
    bus = can.interface.Bus(channel='can0', bustype='socketcan')

    frames = create_frames()

    for frame_id, data in frames:
        msg = can.Message(arbitration_id=frame_id, data=data, is_extended_id=False)
        bus.send(msg)
        print(f"Sent frame 0x{frame_id:X}: {data.hex()}")
        time.sleep(0.1)


if __name__ == '__main__':
    main()
