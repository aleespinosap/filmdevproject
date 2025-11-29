#tempcontrol.py
#Author: Scott Campbell (https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/) with small tweaks by Alejandra Espinosa
#This program uses the ds18b20 sensor to read temperature

import os
import glob
import time
import threading

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

devices = glob.glob(base_dir + '28*')
device_file = devices[0] + '/w1_slave'

actual_temp = None

def read_temp_raw():
    with open(device_file, 'r') as f:
        return f.readlines()
    
def temp_celsius():
    
    lines = read_temp_raw()
    
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.05)
        lines = read_temp_raw()
        
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
  
        return temp_c
    
    return None

def periodic_temp():
    
    global actual_temp
    
    while True:
        temp = temp_celsius()
        
        if temp is not None:
            actual_temp = temp
        
        time.sleep(1)
        
flow = threading.Thread(target = periodic_temp, daemon = True)
flow.start()








