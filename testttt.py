import os
import glob
from pathlib import Path
import sys
import time
from time import sleep

BASE_DIR = Path(__file__).resolve().parent
LCD_DIR = BASE_DIR.parent.parent / "lcd"

sys.path.append(str(LCD_DIR))

import drivers

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

display = drivers.Lcd()

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_celsius():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    
def read_temp_fahrenheit():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f
try:
    while True:
        print(read_temp_celsius())
        print(read_temp_fahrenheit())
        print("Writing to display")
        display.lcd_display_string(f"Temp in C: {str(read_temp_celsius())}",1) 
        display.lcd_display_string(f"Temp in F: {str(read_temp_fahrenheit())}",2)  
        sleep(1)                                   
        display.lcd_clear()                                
      
except KeyboardInterrupt:
    # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
    print("Cleaning up!")
    display.lcd_clear()
