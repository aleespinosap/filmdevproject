#statecontrol.py
#Author: Alejandra Espinosa
#This program controls a sequence of timers for film development

import time
import sys
from pathlib import Path
from gpiozero import Button, LED
import ledcontrol
import tempcontrol

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
dev = 7.5*60
stopbath = 60
fixer = 5*60
photoflo = 30

def cleanup():
    ledcontrol.leds_off()
    display.lcd_clear()
    key1.close()
    key2.close()
    key3.close()
    key4.close()
    
    
def timer(stage: str, duration: int):
    display.lcd_clear()
    start = time.monotonic()
    fin = start + duration
    
    while True:
        timeremaining = fin - time.monotonic()
        if timeremaining <= 0:
            break
        mins, sec = divmod(int(round(timeremaining)), 60)
        display.lcd_display_string(stage, 1)
        display.lcd_display_string(f"{mins:02}:{sec:02} left", 3)
        
        temp = tempcontrol.actual_temp
        if temp is not None:
            display.lcd_display_string(f"Temperature: {temp:4.1f} C", 2)
        else:
            display.lcd_display_string("Temperature: unknown", 2)
            
        time.sleep(max(0, 1 - (time.monotonic() % 1)))
        
    ledcontrol.leds_off()
    display.lcd_clear()
    time.sleep(0.5)
    
  
def welcome_screen():
    display.lcd_display_string("********************", 1)
    display.lcd_display_string("* Press 1 to begin *", 2)
    display.lcd_display_string("*                  *", 3)
    display.lcd_display_string("********************", 4)
    
def process_screen():
    display.lcd_display_string("     Stage done!    ", 1)
    display.lcd_display_string("To continue, press: ", 2)
    display.lcd_display_string("1.Dev     3.Fixer", 3)
    display.lcd_display_string("2.Stop    4.Photoflo", 4)
    
def end_screen():
    display.lcd_display_string("You're all done!", 1)
    display.lcd_display_string("Press: ", 2)
    display.lcd_display_string("1 or 2 to restart", 3)
    display.lcd_display_string("3 or 4 to exit", 4)
    
    while True:
        if key1.is_pressed or key2.is_pressed:
            display.lcd_clear()
            return "main_screen"
        if key3.is_pressed or key4.is_pressed:
            display.lcd_clear()
            return "exit"
            
        time.sleep(0.01)
    
def wash_dev():
    ledcontrol.green_done()
    
    ledcontrol.blue_cycle(short_rinse)
    timer("First rinse", short_rinse)
    time.sleep(3)
    
    ledcontrol.yellow_cycle(dev)
    timer("Stage 1. Developer", dev)
    
    ledcontrol.green_cycle()
    
def stopdev():
    ledcontrol.green_done()
    
    ledcontrol.yellow_cycle(stopbath)
    timer("Stage 2. Stop bath", stopbath)
    
    ledcontrol.green_cycle()
    
def wash_fix():
    ledcontrol.green_done()
    
    ledcontrol.blue_cycle(short_rinse)
    timer("Second rinse", short_rinse)
    time.sleep(3)
    
    ledcontrol.yellow_cycle(fixer)
    timer("Stage 3. Fixer", fixer)
    
    ledcontrol.green_cycle()
    
def wash_photoflo():
    ledcontrol.green_done()
    
    ledcontrol.blue_cycle(long_rinse)
    timer("Final rinse", long_rinse)
    time.sleep(3)
    
    timer("Stage 4. Photoflo", photoflo)
    
    ledcontrol.green_cycle()

def main():
    
    welcome_screen()
    
    try:      
        while True:
            
            if key1.is_pressed:
                wash_dev()
                process_screen()
                while key1.is_pressed:
                    time.sleep(0.05)
                    
            if key2.is_pressed:
                stopdev()
                process_screen()
                while key2.is_pressed:
                    time.sleep(0.05)
                    
            if key3.is_pressed:
                wash_fix()
                process_screen()
                while key3.is_pressed:
                    time.sleep(0.05)
                    
            if key4.is_pressed:
                wash_photoflo()
                result = end_screen()
                
                while key1.is_pressed or key2.is_pressed or key3.is_pressed or key4.is_pressed:
                    time.sleep(0.05)
                
                if result == "main_screen":
                    welcome_screen()
                    continue
                
                elif result == "exit":
                    return
    
            time.sleep(0.05)
   
    except KeyboardInterrupt:
        display.lcd_clear()
        ledcontrol.leds_off()
        
    finally:
        cleanup()

if __name__ == "__main__":
    main()
