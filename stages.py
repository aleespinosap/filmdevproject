# stages.py
import time
import ledcontrol
import tempcontrol


class Stages:
    def __init__(self, ui):
        self.ui = ui

        self.short_rinse = 10
        self.long_rinse  = 60
        self.dev         = 60
        self.stopbath    = 60
        self.fixer       = 45
        self.photoflo    = 30

        self.longpress_time = 1.2  

    def timer(self, label, duration, active_button):
        self.ui.clear()

        remaining = float(duration)
        last_time = time.monotonic()
        press_start = None

        while remaining > 0:
            now = time.monotonic()

            btn = self.ui.detect_button()
            if btn == active_button:
                if press_start is None:
                    press_start = now
                elif now - press_start >= self.longpress_time:
                    ledcontrol.pause_on()      
                    ledcontrol.green_blink()    
                    self.ui.paused_screen()

                    resume_press_start = None

                    while True:
                        now2 = time.monotonic()
                        btn2 = self.ui.detect_button()

                        if btn2 == active_button:
                            if resume_press_start is None:
                                resume_press_start = now2
                            elif now2 - resume_press_start >= self.longpress_time:
                                break
                        else:
                            resume_press_start = None

                        time.sleep(0.05)

                    ledcontrol.green_blink_stop()  
                    ledcontrol.pause_off()         
                    self.ui.clear()

                    last_time = time.monotonic()
                    press_start = None
                    continue
            else:
                press_start = None

            dt = now - last_time
            if dt < 0:
                dt = 0
            remaining -= dt
            last_time = now

            if remaining <= 0:
                break

            mins, secs = divmod(int(remaining), 60)

            self.ui.write_line(label, 1)
            self.ui.write_line(f"{mins:02}:{secs:02} left", 3)

            temp = tempcontrol.actual_temp
            if temp is not None:
                self.ui.write_line(f"Temp: {temp:4.1f} C", 2)
            else:
                self.ui.write_line("Temp: unknown", 2)

            time.sleep(0.3)

        ledcontrol.leds_off()
        self.ui.clear()
        time.sleep(0.5)


    def wash_dev(self):
        ledcontrol.green_done()
        
        ledcontrol.blue_cycle(self.short_rinse)
        self.timer("     First rinse    ", self.short_rinse, active_button=1)
        self.ui.write_line("     Hold 1 to pause", 4)
        
        ledcontrol.yellow_cycle(self.dev)
        self.timer("    Developing...  ", self.dev, active_button=1)

        ledcontrol.green_cycle() 

    def stopdev(self):
        ledcontrol.green_done()

        self.ui.write_line("     Hold 2 to pause", 4)
        
        ledcontrol.yellow_cycle(self.stopbath)
        self.timer("     Stop bath    ", self.stopbath, active_button=2)

        ledcontrol.green_cycle()

    def wash_fix(self):
        ledcontrol.green_done()

        self.ui.write_line("     Hold 3 to pause", 4)
        
        ledcontrol.blue_cycle(self.short_rinse)
        self.timer("    Second rinse    ", self.short_rinse, active_button=3)

        ledcontrol.yellow_cycle(self.fixer)
        self.timer("     Fixing...    ", self.fixer, active_button=3)

        ledcontrol.green_cycle()

    def wash_photoflo(self):
        ledcontrol.green_done()
        
        self.ui.write_line("     Hold 4 to pause", 4)
        
        ledcontrol.blue_cycle(self.long_rinse)
        self.timer("    Final rinse    ", self.long_rinse, active_button=4)

        self.timer("      Photoflo      ", self.photoflo, active_button=4)

        ledcontrol.green_cycle()

