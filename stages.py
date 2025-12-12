# stages.py

import math
import time
import ledcontrol
import tempcontrol


class Stages:
    
    """
    This class contains all the logic pertaining the timers used across every stage
    as well as the stage-dependent LED behavior. Pausing is handled in here, and the
    temperature display is too
    """
    
    def __init__(self, ui):
        self.ui = ui

        self.short_rinse = 60    #The timer durations are hard coded because they don't change in B&W dev. Only Dev timer can change which is handled elsewhere
        self.long_rinse  = 5*60
        self.dev         = 60
        self.stopbath    = 60
        self.fixer       = 5.5*60
        self.photoflo    = 30

        self.longpress_time = 1.2 #Long press corresponds to button handling for pausing

        self.push_pull_options = [ #These are (stops of light, factor)
            (-2, 0.6),			   #A stop of light is by how much should the film be pushed or pulled, the factor is by how much the timer has to be adjusted
            (-1, 0.8),
            (0, 1.0),
            (1, 1.2),
            (2, 1.4),
        ]
        self.dev_run_seconds = self.dev
        self.dev_choice_level = 0

    def set_dev_settings(self, base_seconds: int, choice_level: int):
        """Set development timer and push/pull level.

        Configures the development stage duration based on the user's choice
        of exposure compensation (push/pull processing).

        Args:
            base_seconds (int): Base development time in seconds before push/pull adjustment.
            choice_level (int): Index into push_pull_options list (-2 to +2 stops).
        """
        self.dev_run_seconds = max(10, int(base_seconds))
        self.dev_choice_level = choice_level

    def timer(self, label, duration, active_button):
        """Run a countdown timer for a development stage with pause support.

        Updates the LCD display every second showing remaining time and current
        temperature. Monitors the specified button for long-press (1.2s) to pause
        and resume. Maintains timer accuracy across pause/resume cycles.

        Args:
            label (str): Stage name displayed on LCD line 1 (max 20 chars).
            duration (float): Stage duration in seconds.
            active_button (int): Button number (1-4) that controls pause for this stage.
        """
        self.ui.clear()

        end_time = time.monotonic() + float(duration)
        press_start = None
        pause_start = None
        last_displayed_seconds = None
       
        pause_hint = f"Hold {active_button} to pause"    # Hint shown on the fourth LCD line to remind which button pauses this stage

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
            
        """
        Handles the full Stage 1 process: pre-soak followed by development.
        The pre-soak uses a blue PWM LED, while development uses a yellow
        flashing LED pattern. A solid green LED indicates completion of
        development.
        """
        
        ledcontrol.green_done()

        ledcontrol.blue_cycle(self.short_rinse)
        self.timer("      Pre-Soak      ", self.short_rinse, active_button=1)

        dev_duration = int(round(self.dev_run_seconds))
        dev_label = "Developing..."

        level_display = f"+{self.dev_choice_level}" if self.dev_choice_level > 0 else str(self.dev_choice_level)
        padded_label = dev_label[: (20 - len(level_display))].ljust(20 - len(level_display)) + level_display.rjust(len(level_display))

        ledcontrol.yellow_cycle(dev_duration)
        self.timer(padded_label, dev_duration, active_button=1)

        ledcontrol.green_cycle()

    def stopdev(self):
        
        """
        Handles the stop bath stage.
        Runs a fixed-length timer with yellow LED activity and allows pause
        via long button press. A solid green LED indicates completion.
        """
        
        ledcontrol.green_done()

        ledcontrol.yellow_cycle(self.stopbath)
        self.timer("     Stop bath    ", self.stopbath, active_button=2)

        ledcontrol.green_cycle()

    def wash_fix(self):
        
        """
        Handles the rinse followed by fixer stage.
        The rinse uses a blue PWM LED, while the fixer uses yellow LED activity.
        A solid green LED indicates completion of the fixer stage.
        """
        
        ledcontrol.green_done()

        ledcontrol.blue_cycle(self.short_rinse)
        self.timer("    Second rinse    ", self.short_rinse, active_button=3)

        ledcontrol.yellow_cycle(self.fixer)
        self.timer("     Fixing...    ", self.fixer, active_button=3)

        ledcontrol.green_cycle()

    def wash_photoflo(self):
        
        """
        Handles the final rinse and photoflo stage.
        Blue PWM LED is used during the final rinse. Photoflo does not use
        yellow LED activity. A solid green LED indicates final completion.
        """
        
        ledcontrol.green_done()

        ledcontrol.blue_cycle(self.long_rinse)
        self.timer("    Final rinse    ", self.long_rinse, active_button=4)

        self.timer("      Photoflo      ", self.photoflo, active_button=4)

        ledcontrol.green_cycle()
