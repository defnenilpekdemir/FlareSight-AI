# Required Libraries and Modules
from pybricks.hubs import InventorHub  # Import the InventorHub class from the PyBricks library.
from pybricks.pupdevices import Motor   # Import the Motor class from the PyBricks library.
from pybricks.parameters import Port     # Used to specify the port to which devices are connected.
from pybricks.tools import wait          # Used to wait for a specified duration (in milliseconds).

# Standard MicroPython modules.
from usys import stdin, stdout           # Used for reading input from the user and writing output to the screen.
from uselect import poll                 # Used to efficiently monitor multiple sources.

# Motor and Hub Definitions
# Define the connection ports for the motor and hub devices.
motor = Motor(Port.A)
hub = InventorHub

# Setting Up the Polling Mechanism
# Used to wait for incoming data.
keyboard = poll()
keyboard.register(stdin)

# Main Loop
while True:
    # Indicates to the remote program that it is ready for a command.
    stdout.buffer.write(b"rdy")
    
    # Input Waiting
    # Waits for input from the user; if there is no input, waits 10 ms and checks again.
    while not keyboard.poll(0):
        wait(10)
    
    # Processing Commands
    cmd = stdin.buffer.read(3)
    # Determines what action to take based on the command.
    if cmd == b"fwd":
        motor.dc(30)
    elif cmd == b"stp":
        motor.stop()
    elif cmd == b"rev":
        motor.dc(-60)
    elif cmd == b"bye":
        break
    else:
        motor.stop()  # Stops the motor for unknown commands.
