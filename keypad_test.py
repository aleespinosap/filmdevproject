"""
This Raspberry Pi code was developed by newbiely.com
This Raspberry Pi code is made available for public use without any restriction
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-keypad-1x4
"""

from gpiozero import Button
from time import sleep

# Define GPIO pins for the keypad buttons
PIN_KEY_1 = 25 # The Raspberry Pi pin GPIO24 connected to the key 1
PIN_KEY_2 = 8  # The Raspberry Pi pin GPIO23 connected to the key 2
PIN_KEY_3 = 23 # The Raspberry Pi pin GPIO8  connected to the key 3
PIN_KEY_4 = 24 # The Raspberry Pi pin GPIO25 connected to the key 4

# Create Button objects for each key
key_1 = Button(PIN_KEY_1, pull_up=True)
key_2 = Button(PIN_KEY_2, pull_up=True)
key_3 = Button(PIN_KEY_3, pull_up=True)
key_4 = Button(PIN_KEY_4, pull_up=True)

# List of button objects
key_buttons = [key_1, key_2, key_3, key_4]

# Debounce time (in seconds)
DEBOUNCE_TIME = 0.1

# Function to handle key press events
def key_pressed(key):
    print(f"The key {key} is pressed")

# Attach event listeners for each button press
key_1.when_pressed = lambda: key_pressed(1)
key_2.when_pressed = lambda: key_pressed(2)
key_3.when_pressed = lambda: key_pressed(3)
key_4.when_pressed = lambda: key_pressed(4)

try:
    while True:
        sleep(0.1)  # Just keep the program running to detect key presses

except KeyboardInterrupt:
    print("Program terminated")