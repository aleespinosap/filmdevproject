# relaycontrol.py
# Controls heater relay using DS18B20 temperature readings from tempcontrol.py


# Heater ON < 20°C (68°F)
# Heater OFF > 21°C (70°F)

from gpiozero import OutputDevice
import threading
import time
import tempcontrol 

HEAT_ON_C  = 20.0   # 68°F
HEAT_OFF_C = 21.0   # 70°F


heater = OutputDevice(16, active_high=True, initial_value=False)

def update_heater():
    temp = tempcontrol.actual_temp

    if temp is None:
        heater.off()
        return

    if temp < HEAT_ON_C:
        heater.on()

    elif temp > HEAT_OFF_C:
        heater.off()

def _relay_loop():
    while True:
        update_heater()
        time.sleep(1)  

def start():
    """Start heater thread once at program startup."""
    t = threading.Thread(target=_relay_loop, daemon=True)
    t.start()
    return t


def stop():
    """Turn heater off on program exit."""
    heater.off()
