import time
from gpiozero import RotaryEncoder, Button


class RotaryControl:

    def __init__(self, pin_a=5, pin_b=6, button_pin=12, debounce=0.1):
        self.encoder = RotaryEncoder(pin_a, pin_b, max_steps=0, wrap=False)
        self.button = Button(button_pin, pull_up=True, bounce_time=debounce)
        self._last_steps = self.encoder.steps

    def delta(self):
        current = self.encoder.steps
        change = current - self._last_steps
        self._last_steps = current
        return change

    def is_pressed(self):
        return self.button.is_pressed

    def wait_for_press(self):
        while not self.button.is_pressed:
            time.sleep(0.02)

    def close(self):
        self.encoder.close()
        self.button.close()
