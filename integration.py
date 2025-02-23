# Required Libraries and Modules
import asyncio
import json
from contextlib import suppress
from bleak import BleakScanner, BleakClient

# Constants and State Variables
# We define constants (e.g., hub name, UUID) and variables to control the state of the motor.
HUB_NAME = "PH1"
CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
# Threshold value (example: 1)
KP_THRESHOLD = 5
# Motor state:
# None => 'fwd' has not been executed yet
# True => 'fwd' has been executed; do not execute 'fwd' again
clossed = None
# Counter for iterations below the threshold (increases when Kp < threshold)
below_count = 0

# Function to Read Kp Value from TXT Files
# Reads .txt files (in JSON format) and calculates the Kp value based on alpha and beta values.
async def get_kp_value_from_txt(
    magneto_path="magnetogram_result.txt",
    continuum_path="continuum_result.txt",
) -> float:
    """
    Reads JSON-formatted data from .txt files and checks the values for
    "magnetogram-alpha", "magnetogram-beta", "continuum-alpha", and "continuum-beta".
    Conditions:
     - If both beta > 0.7 => Kp = 6
     - Otherwise, if both alpha > 0.7 => Kp = 2
     - Otherwise => Kp = 0
    """
    try:
        with open(magneto_path, "r", encoding="utf-8") as f1:
            magneto_data = json.load(f1)
        with open(continuum_path, "r", encoding="utf-8") as f2:
            continuum_data = json.load(f2)
        m_alpha = magneto_data.get("magnetogram-alpha", 0)
        m_beta = magneto_data.get("magnetogram-beta", 0)
        c_alpha = continuum_data.get("continuum-alpha", 0)
        c_beta = continuum_data.get("continuum-beta", 0)
        if m_beta > 0.7 and c_beta > 0.7:
            return 6
        elif m_alpha > 0.7 and c_alpha > 0.7:
            return 2
        else:
            return 0
    except Exception as e:
        print(f"[!] Error reading alpha/beta from TXT (JSON) files: {e}")
        return 0

# Command Sending Function
# Used to send a command to the hub via a Bluetooth connection.
async def send_command(client: BleakClient, data: bytes):
    # A simple function to send a command (stdin) to the hub.
    await client.write_gatt_char(CHAR_UUID, b"\x06" + data, response=True)

# Main Program Flow
# Uses asyncio to establish a connection with the hub, processes incoming and outgoing commands,
# and controls the motor based on the Kp value.
async def main():
    global clossed, below_count
    print("[i] Searching for:", HUB_NAME)
    device = await BleakScanner.find_device_by_name(HUB_NAME)
    if not device:
        print(f"[!] Could not find a hub named '{HUB_NAME}'.")
        return

# Handling Disconnection
# Defines the operation to execute when the connection with the hub is lost.
def handle_disconnect(_):
    # Triggered when the connection is lost.
    print("[!] Hub was disconnected.")

# Main Function
# Establishes the hub connection, processes incoming and outgoing commands, controls the motor based on the Kp value,
# and ensures that the connection is closed properly.
async def main():
    global clossed, below_count
    print("[i] Searching for:", HUB_NAME)
    device = await BleakScanner.find_device_by_name(HUB_NAME)
    if not device:
        print(f"[!] Could not find a hub named '{HUB_NAME}'.")
        return
    client = BleakClient(device, handle_disconnect)
    print("[i] Connecting to the hub...")
    await client.connect()
    if not client.is_connected:
        print("[!] Connection failed!")
        return
    print("[i] Hub connected! Don't forget to start your code on the PyBricks side using the button.")
    
    async def handle_rx(_, data: bytearray):
        if data and data[0] == 0x01:
            payload = data[1:]
            print(f"[Hub Output] {payload}")
    
    # Start listening to the hub's stdout output.
    await client.start_notify(CHAR_UUID, handle_rx)
    print("[i] Program is starting. Every 60 seconds, alpha/beta values will be read from .txt files (JSON format).")
    print("[i] Conditions:")
    print(" - If both beta > 0.7 => Kp = 6")
    print(" - Otherwise, if both alpha > 0.7 => Kp = 2")
    print(" - Otherwise => Kp = 0")
    print("[i] When Kp >= 1, the 'fwd' command is triggered. If Kp remains low for 10 minutes, 'rev' is executed.")
    print("[i] Press Ctrl + C to exit.")
    
    try:
        while True:
            # 1) Read the alpha/beta values from the .txt files and calculate Kp.
            kp_val = await get_kp_value_from_txt(
                "magnetogram_result.txt",
                "continuum_result.txt"
            )
            print(f"[i] Current Kp value (from TXT): {kp_val}")
            # 2) Compare Kp with the threshold.
            if kp_val >= KP_THRESHOLD:
                print(f"[i] Kp={kp_val} >= {KP_THRESHOLD}")
                # If 'fwd' has not been executed yet (clossed is None), execute 'fwd' now.
                if clossed is None:
                    print("[!] Sending 'fwd' command (5 seconds)...")
                    await send_command(client, b"fwd")
                    await asyncio.sleep(5)
                    await send_command(client, b"stp")
                    print("[!] Motor stopped. Setting clossed=True")
                    clossed = True
                else:
                    # If clossed is True, do not send 'fwd' again.
                    print("[i] 'clossed' is True, not sending 'fwd' a second time.")
                    # Reset the below-threshold counter since Kp is above the threshold.
                    below_count = 0
            else:
                # When Kp is below the threshold.
                below_count += 1
                print(f"[i] Kp={kp_val} < {KP_THRESHOLD}, below_count = {below_count}")
                # Only if 'fwd' has been executed (clossed is True) and Kp remains low for 10 iterations (minutes),
                # send the 'rev' command.
                if clossed is True and below_count >= 10:
                    print("[!] Kp has been low for 10 minutes => Sending 'rev' (5 sec) + 'stp', then setting clossed=None")
                    await send_command(client, b"rev")
                    await asyncio.sleep(5)
                    await send_command(client, b"stp")
                    print("[!] 'rev' completed, setting clossed=None.")
                    clossed = None
                    below_count = 0
            # Wait here for 60 seconds (for testing purposes). Use 600 seconds to check every 10 minutes.
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        print("[i] main() cancelled!")
    except KeyboardInterrupt:
        print("\n[i] Interrupted by user (Ctrl + C).")
        print("[i] Program terminating, disconnecting from the hub...")
        await client.disconnect()

# Running the Program
# The program is executed in the '__main__' block. The main loop is started and the hub connection is established.
if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())
