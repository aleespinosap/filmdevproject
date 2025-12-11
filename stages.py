# stages.py
import math
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

        end_time = time.monotonic() + float(duration)
        press_start = None
        pause_start = None
        last_displayed_seconds = None
        # Hint shown on the fourth LCD line to remind which button pauses this stage
        pause_hint = f"Long press {active_button} = pause"

        while True:
            now = time.monotonic()
            remaining = end_time - now

            if remaining <= 0:
                break

            # Button handling
            btn = self.ui.detect_button()
            if btn == active_button:
                if press_start is None:
                    press_start = now
                elif now - press_start >= self.longpress_time:
                    ledcontrol.pause_on()
                    ledcontrol.green_blink()
                    self.ui.paused_screen()

                    pause_start = time.monotonic()
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

                    if pause_start is not None:
                        paused_duration = time.monotonic() - pause_start
                        end_time += paused_duration
                        pause_start = None

                    ledcontrol.green_blink_stop()
                    ledcontrol.pause_off()
                    self.ui.clear()

                    press_start = None
                    continue
            else:
                press_start = None

            display_seconds = max(0, math.ceil(remaining))

            if display_seconds != last_displayed_seconds:
                mins, secs = divmod(display_seconds, 60)

                self.ui.write_line(label, 1)
                self.ui.write_line(f"{mins:02}:{secs:02} left", 3)

                temp = tempcontrol.actual_temp
                if temp is not None:
                    self.ui.write_line(f"Temp: {temp:4.1f} C", 2)
                else:
                    self.ui.write_line("Temp: unknown", 2)

                self.ui.write_line(pause_hint, 4)

                last_displayed_seconds = display_seconds

            # Sleep in short bursts until the next second tick so the display changes
            # exactly once per second while staying responsive to pauses.
            next_tick = end_time - (display_seconds - 1)
            remaining_to_tick = next_tick - time.monotonic()

            if remaining_to_tick <= 0:
                time.sleep(0.02)
            else:
                time.sleep(max(0.02, min(0.1, remaining_to_tick)))

        ledcontrol.leds_off()
        self.ui.clear()
        time.sleep(0.5)


    def wash_dev(self):
        ledcontrol.green_done()

        ledcontrol.blue_cycle(self.short_rinse)
        self.timer("     First rinse    ", self.short_rinse, active_button=1)

        ledcontrol.yellow_cycle(self.dev)
        self.timer("    Developing...  ", self.dev, active_button=1)

        ledcontrol.green_cycle()

    def stopdev(self):
        ledcontrol.green_done()

        ledcontrol.yellow_cycle(self.stopbath)
        self.timer("     Stop bath    ", self.stopbath, active_button=2)

        ledcontrol.green_cycle()

    def wash_fix(self):
        ledcontrol.green_done()

        ledcontrol.blue_cycle(self.short_rinse)
        self.timer("    Second rinse    ", self.short_rinse, active_button=3)

        ledcontrol.yellow_cycle(self.fixer)
        self.timer("     Fixing...    ", self.fixer, active_button=3)

        ledcontrol.green_cycle()

    def wash_photoflo(self):
        ledcontrol.green_done()

        ledcontrol.blue_cycle(self.long_rinse)
        self.timer("    Final rinse    ", self.long_rinse, active_button=4)

        self.timer("      Photoflo      ", self.photoflo, active_button=4)

        ledcontrol.green_cycle()

