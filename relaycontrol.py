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
stop_event = threading.Event()
_worker = None

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
    while not stop_event.is_set():
        update_heater()
        time.sleep(1)

def start():
    """Start heater thread once at program startup."""
    global _worker

    if _worker and _worker.is_alive():
        return _worker

    stop_event.clear()
    _worker = threading.Thread(target=_relay_loop, daemon=True)
    _worker.start()
    return _worker


def stop():
    """Turn heater off on program exit."""
    stop_event.set()
    if _worker and _worker.is_alive():
        _worker.join(timeout=1.5)
    heater.off()
    heater.close()
