#ledcontrol.py
#Author: Alejandra Espinosa
#This program controls the led sequence for the film dev project

from gpiozero import LED, PWMLED
from time import sleep, time
import threading

blue = PWMLED(17)
yellow = LED(27)
green = LED(22)

stop_flag = False

def leds_off():
    global stop_flag
    stop_flag = True
    yellow.off()
    blue.off()
    
def rerun_stop_flag():
    global stop_flag
    stop_flag = False
    
def blue_threading(duration):
    fin = time() + duration
    
    while time() < fin and not stop_flag:
        for i in range(0,101):
            if stop_flag or time() >= fin:
                break
            blue.value = i/100 #agregar else?
            sleep(0.01)
        for i in range(100,-1,-1):
            if stop_flag or time() >= fin:
                break
            blue.value = i/100 #agregar else?
            sleep(0.01)
    blue.off()
    
def blue_cycle(duration):
    rerun_stop_flag()
    flow = threading.Thread(target=blue_threading, args=(duration,))
    flow.daemon = True
    flow.start()
    
    return flow

def yellow_threading(duration):
    fin = time() + duration
    
    while time() < fin and not stop_flag:
        for i in range(10):
            if stop_flag or time() >= fin:
                break
            yellow.on()
            sleep(0.5)
            yellow.off()
            sleep(0.5)
            
        cycle_fin = time() + 20
        while time() < cycle_fin:
            if stop_flag or time() >= fin:
                break
            sleep(0.1)
    yellow.off()
    
def yellow_cycle(duration):
    rerun_stop_flag()
    flow = threading.Thread(target=yellow_threading, args=(duration,))
    flow.daemon = True
    flow.start()
    
    return flow    
    
def green_cycle():
    green.on()
    
def green_done():
    green.off()
    
        
    