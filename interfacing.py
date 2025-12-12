# interfacing.py
import sys
import time
from pathlib import Path
from gpiozero import Button
from rotarycontrol import RotaryControl

# LCD driver import
BASE_DIR = Path(__file__).resolve().parent

def _extend_sys_path_for_lcd(base_dir: Path):
    """
    This function was made by AI. I asked it if there was anything it would change from my code
    and it suggested this function so here it is.
    Add the most likely lcd driver directory to sys.path.

    Prefer an adjacent `lcd/` folder but fall back to the historical
    `../../lcd` location for compatibility with older deployments.
    """

    lcd_candidates = [
        base_dir / "lcd",              # ./lcd
        base_dir.parent / "lcd",       # ../lcd
        base_dir.parent.parent / "lcd" # ../../lcd (legacy)
    ]

    for candidate in lcd_candidates:
        if candidate.is_dir():
            sys.path.append(str(candidate))
            break
    else:
        # Preserve previous behavior if no candidate directory is present.
        sys.path.append(str(lcd_candidates[-1]))


_extend_sys_path_for_lcd(BASE_DIR)

import drivers


class UI:
    
    """
    Handles all user interaction including:
    - LCD output (all the different screens shown to the user)
    - Button input (detect_button looks for which button is being pushed)
    - Rotary encoder input for setting dev time and push or pull setting

    This class acts as the interface layer between the user and the
    development logic.
    """
    
    def __init__(self):
        self.display = drivers.Lcd()

        self.rotary = RotaryControl()

        self.key1 = Button(25, pull_up=True, bounce_time=0.1)
        self.key2 = Button(8,  pull_up=True, bounce_time=0.1)
        self.key3 = Button(23, pull_up=True, bounce_time=0.1)
        self.key4 = Button(24, pull_up=True, bounce_time=0.1)

    @staticmethod
    def _line(text: str) -> str:

        return text[:20].ljust(20)

    def write_line(self, text: str, line: int):
        self.display.lcd_display_string(self._line(text), line)

    def clear(self):
        self.display.lcd_clear()

    def _format_time(self, seconds: int) -> str:
        mins, secs = divmod(max(0, int(seconds)), 60)
        return f"{mins:02}:{secs:02}"

    def welcome_screen(self):
        self.clear()
        self.write_line("********************", 1)
        self.write_line("*     Welcome!     *", 2)
        self.write_line("* Press 1 to begin *", 3)
        self.write_line("********************", 4)

    def stage_done_screen(self):
        self.clear()
        self.write_line("   Stage finished   ", 1)
        self.write_line(" Choose next stage: ", 2)
        self.write_line("1 Dev   3 Fixer    ", 3)
        self.write_line("2 Stop  4 Photoflo ", 4)

    def paused_screen(self):
        self.clear()
        self.write_line("********************", 1)
        self.write_line("*      PAUSED      *", 2)
        self.write_line("*  Hold to resume  *", 3)
        self.write_line("********************", 4)

    def development_settings(self, base_seconds: int, push_pull_options, current_level=0):
        
        """
        Allows the user to configure development time and push/pull level
        using the rotary encoder.
    
        Returns the adjusted development time and selected push/pull level.
        """

        def format_level(level: int) -> str:
            return f"+{level}" if level > 0 else str(level)

        def show_time(value):
            self.clear()
            self.write_line("[ Dev time ]", 1)
            self.write_line(f"   {self._format_time(value)}   ", 2)
            self.write_line("Rotate to adjust", 3)
            self.write_line("Press knob to set", 4)

        def show_push_pull(index):
            level, _ = push_pull_options[index]
            self.clear()
            self.write_line("Push/Pull setting", 1)
            self.write_line(f"Level: {format_level(level).rjust(3)}", 2)
            self.write_line("Rotate to adjust", 3)
            self.write_line("Press knob to set", 4)

        # Adjusts base development time in 5s increments
        value = max(10, int(base_seconds))
        show_time(value)

        while True:
            delta = self.rotary.delta()
            if delta:
                value = min(3600, max(10, value + delta * 5))
                show_time(value)

            if self.rotary.is_pressed():
                time.sleep(0.15)  # debounces the confirmation
                break

            time.sleep(0.05)

        # Choose push/pull level
        index = 0 
        for i, (level, _) in enumerate(push_pull_options):
            if level == current_level:
                index = i
                break
        show_push_pull(index)

        while True:
            delta = self.rotary.delta()
            if delta:
                index = (index + delta) % len(push_pull_options)
                show_push_pull(index)

            if self.rotary.is_pressed():
                time.sleep(0.15)
                break

            time.sleep(0.05)

        level, factor = push_pull_options[index]
        adjusted = int(round(value * factor))

        self.clear()
        self.write_line("Dev settings ready", 1)
        self.write_line(f"Time: {self._format_time(adjusted)}", 2)
        self.write_line(f"Push/Pull: {format_level(level).rjust(3)}", 3)
        self.write_line("Press knob to start", 4)

        # Wait for confirmation so user can see what they chose before starting.
        while not self.rotary.is_pressed():
            time.sleep(0.05)
        time.sleep(0.15)  # debouncing

        return adjusted, level

    def end_screen(self):
        self.clear()
        self.write_line("  You're all done!  ", 1)
        self.write_line("--------------------", 2)
        self.write_line(" Press any button   ", 3)
        self.write_line("   to restart       ", 4)

        self.wait_for_button()
        return "restart"

    def detect_button(self):
        
    """
    Checks which stage button is currently pressed.
    Returns the button number (1–4) or None if no button is pressed.
    """
        
        if self.key1.is_pressed:
            return 1
        if self.key2.is_pressed:
            return 2
        if self.key3.is_pressed:
            return 3
        if self.key4.is_pressed:
            return 4
        return None

    def wait_for_button(self):
        while True:
            b = self.detect_button()
            if b:
                return b
            time.sleep(0.02)

    def cleanup(self):
        self.clear()
        self.key1.close()
        self.key2.close()
        self.key3.close()
        self.key4.close()
        self.rotary.close()

