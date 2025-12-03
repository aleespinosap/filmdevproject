# interfacing.py
import sys
import time
from pathlib import Path
from gpiozero import Button

# LCD driver import
BASE_DIR = Path(__file__).resolve().parent
LCD_DIR = BASE_DIR.parent.parent / "lcd"
sys.path.append(str(LCD_DIR))

import drivers


class UI:
    def __init__(self):
        self.display = drivers.Lcd()

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

    def end_screen(self):
        self.clear()
        self.write_line("  You're all done!  ", 1)
        self.write_line("--------------------", 2)
        self.write_line("    1/2 Restart     ", 3)
        self.write_line("    3/4 Exit        ", 4)

        while True:
            if self.key1.is_pressed or self.key2.is_pressed:
                return "restart"
            if self.key3.is_pressed or self.key4.is_pressed:
                return "exit"
            time.sleep(0.02)

    def detect_button(self):
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
