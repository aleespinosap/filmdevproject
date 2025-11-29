#statecontrol.py
#Author: Alejandra Espinosa
#This program controls a sequence of timers for film development

import time
import sys
from pathlib import Path
from gpiozero import Button, LED
import ledcontrol

BASE_DIR = Path(__file__).resolve().parent
LCD_DIR = BASE_DIR.parent.parent / "lcd"   
sys.path.append(str(LCD_DIR))

import drivers

display = drivers.Lcd()

#define which gpio pins each key is in
pkey1 = 25
pkey2 = 8
pkey3 = 23
pkey4 = 24

key1 = Button(pkey1, pull_up=True, bounce_time=0.1)
key2 = Button(pkey2, pull_up=True, bounce_time=0.1)
key3 = Button(pkey3, pull_up=True, bounce_time=0.1)
key4 = Button(pkey4, pull_up=True, bounce_time=0.1)

#timer durations, hard coded for now. all in seconds
short_rinse = 60
long_rinse = 5*60
dev = 7*60
stopbath = 60
fixer = 5*60
photoflo = 30


def timer(stage: str, duration: int):
    fin = time.time() + duration
    
    while True:
        timeremaining = int(fin - time.time())
        if timeremaining <= 0:
            break
        mins, sec = divmod(timeremaining, 60)
        display.lcd_display_string(stage, 1)
        display.lcd_display_string(f"{mins:02}:{sec:02} left", 2)
        time.sleep(1)
        
    ledcontrol.leds_off()
    display.lcd_clear()
    time.sleep(0.5)
    
  
def welcome_screen():
    display.lcd_display_string("Welcome!", 1)
    display.lcd_display_string("Press 1-4", 2)
    
def wash_dev():
    ledcontrol.green_done()
    
    ledcontrol.blue_cycle(short_rinse)
    timer("First rinse", short_rinse)
    time.sleep(3)
    
    ledcontrol.yellow_cycle(dev)
    timer("Developer", dev)
    
    ledcontrol.green_cycle()
    
def stopdev():
    ledcontrol.green_done()
    
    ledcontrol.yellow_cycle(stopbath)
    timer("Stop bath", stopbath)
    
    ledcontrol.green_cycle()
    
def wash_fix():
    ledcontrol.green_done()
    
    ledcontrol.blue_cycle(short_rinse)
    timer("Second rinse", short_rinse)
    time.sleep(3)
    
    ledcontrol.yellow_cycle(fixer)
    timer("Fixer", fixer)
    
    ledcontrol.green_cycle()
    
def wash_photoflo():
    ledcontrol.green_done()
    
    ledcontrol.blue_cycle(long_rinse)
    timer("Final rinse", long_rinse)
    time.sleep(3)
    
    timer("Photoflo", photoflo)
    
    ledcontrol.green_cycle()

def main():
    
    welcome_screen()
    
    try:
        
        while True:
            
            if key1.is_pressed:
                wash_dev()
                welcome_screen()
                while key1.is_pressed:
                    time.sleep(0.05)
                    
            if key2.is_pressed:
                stopdev()
                welcome_screen()
                while key2.is_pressed:
                    time.sleep(0.05)
                    
            if key3.is_pressed:
                wash_fix()
                welcome_screen()
                while key3.is_pressed:
                    time.sleep(0.05)
                    
            if key4.is_pressed:
                wash_photoflo()
                welcome_screen()
                while key4.is_pressed:
                    time.sleep(0.05)
    
            time.sleep(0.05)
   
    except KeyboardInterrupt:
        display.lcd_clear()
        ledcontrol.leds_off()

if __name__ == "__main__":
    main()
