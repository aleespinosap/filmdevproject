#tempcontrol.py
#Author: Scott Campbell (https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/) with small tweaks by Alejandra Espinosa

import os
import glob
import time
import threading

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/' #the temp sensor is here

devices = glob.glob(base_dir + '28*')  #looks for the sensor's directory, it should start with a 28
device_file = devices[0] + '/w1_slave'

actual_temp = None

_stop_event = threading.Event()
_worker = None


def read_temp_raw():
    with open(device_file, 'r') as f: #reads the temperature directly from the file
        return f.readlines()


def temp_celsius():  #after reading the file, this function converts that info into celsius and makes that its return value
    lines = read_temp_raw()

    while lines[0].strip()[-3:] != 'YES':
        if _stop_event.is_set():
            return None
        time.sleep(0.05)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0

        return temp_c

    return None


def _periodic_temp():
    global actual_temp

    while not _stop_event.is_set():
        temp = temp_celsius()

        if temp is not None:
            actual_temp = temp

        _stop_event.wait(1)


def start():
    
    """Start the background temperature monitoring thread in the backrground
    The thread continuously reads data from the DS18B20 sensor and updates
    the global actual_temp variable so other modules can access the
    current temperature in real time.
    """
    
    global _worker
    if _worker and _worker.is_alive():
        return _worker

    _stop_event.clear()
    _worker = threading.Thread(target=_periodic_temp, daemon=True)
    _worker.start()
    return _worker


def cleanup():
    """Stop background temperature thread to help cleanup."""
    _stop_event.set()
    if _worker and _worker.is_alive():
        _worker.join(timeout=1.5)


start()
