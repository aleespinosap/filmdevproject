# # interfacing.py
# import sys
# import time
# from pathlib import Path
# from gpiozero import Button
# 
# # LCD driver import
# BASE_DIR = Path(__file__).resolve().parent
# LCD_DIR = BASE_DIR.parent.parent / "lcd"
# sys.path.append(str(LCD_DIR))
# 
# import drivers
# 
# 
# class UI:
#     def __init__(self):
#         self.display = drivers.Lcd()
# 
#         self.key1 = Button(25, pull_up=True, bounce_time=0.1)
#         self.key2 = Button(8,  pull_up=True, bounce_time=0.1)
#         self.key3 = Button(23, pull_up=True, bounce_time=0.1)
#         self.key4 = Button(24, pull_up=True, bounce_time=0.1)
# 
#     @staticmethod
#     def _line(text: str) -> str:
#         
#         return text[:20].ljust(20)
# 
#     def write_line(self, text: str, line: int):
#         self.display.lcd_display_string(self._line(text), line)
# 
#     def clear(self):
#         self.display.lcd_clear()
# 
#     def welcome_screen(self):
#         self.clear()
#         self.write_line("********************", 1)
#         self.write_line("*     Welcome!     *", 2)
#         self.write_line("* Press 1 to begin *", 3)
#         self.write_line("********************", 4)
# 
#     def stage_done_screen(self):
#         self.clear()
#         self.write_line("   Stage finished   ", 1)
#         self.write_line(" Choose next stage: ", 2)
#         self.write_line("1 Dev   3 Fixer    ", 3)
#         self.write_line("2 Stop  4 Photoflo ", 4)
# 
#     def paused_screen(self):
#         self.clear()
#         self.write_line("********************", 1)
#         self.write_line("*      PAUSED      *", 2)
#         self.write_line("*  Hold to resume  *", 3)
#         self.write_line("********************", 4)
# 
#     def end_screen(self):
#         self.clear()
#         self.write_line("  You're all done!  ", 1)
#         self.write_line("--------------------", 2)
#         self.write_line(" Press any button   ", 3)
#         self.write_line("   to restart       ", 4)
# 
#         self.wait_for_button()
#         return "restart"
#     
#     def detect_button(self):
#         if self.key1.is_pressed:
#             return 1
#         if self.key2.is_pressed:
#             return 2
#         if self.key3.is_pressed:
#             return 3
#         if self.key4.is_pressed:
#             return 4
#         return None
# 
#     def wait_for_button(self):
#         while True:
#             b = self.detect_button()
#             if b:
#                 return b
#             time.sleep(0.02)
# 
#     def cleanup(self):
#         self.clear()
#         self.key1.close()
#         self.key2.close()
#         self.key3.close()
#         self.key4.close()
# interfacing.py
import sys
import time
from pathlib import Path
from gpiozero import Button
from rotarycontrol import RotaryControl

# LCD driver import
BASE_DIR = Path(__file__).resolve().parent

def _extend_sys_path_for_lcd(base_dir: Path):
    """Add the most likely lcd driver directory to sys.path.

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

    def development_settings(self, base_seconds: int, push_pull_options, current_label="Normal"):
        """Use the rotary encoder to set base dev time, then choose push/pull."""

        def show_time(value):
            self.clear()
            self.write_line("Set dev time", 1)
            self.write_line(f"{self._format_time(value)} (mm:ss)", 2)
            self.write_line("Rotate to adjust", 3)
            self.write_line("Press knob to set", 4)

        def show_push_pull(index):
            label, _, factor_label = push_pull_options[index]
            self.clear()
            self.write_line("Push/Pull setting", 1)
            self.write_line(label, 2)
            self.write_line(f"Factor: {factor_label}", 3)
            self.write_line("Press knob to set", 4)

        # Adjust base development time in 5s steps
        value = max(10, int(base_seconds))
        show_time(value)

        while True:
            delta = self.rotary.delta()
            if delta:
                value = min(3600, max(10, value + delta * 5))
                show_time(value)

            if self.rotary.is_pressed():
                time.sleep(0.15)  # debounce the confirmation
                break

            time.sleep(0.05)

        # Choose push/pull level
        index = 1  # default to the neutral option
        for i, (label, _, _) in enumerate(push_pull_options):
            if label == current_label:
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

        label, factor, factor_label = push_pull_options[index]
        adjusted = int(round(value * factor))

        self.clear()
        self.write_line("Dev settings saved", 1)
        self.write_line(f"Base: {self._format_time(value)}", 2)
        self.write_line(f"Mode: {label}", 3)
        self.write_line(f"Run: {self._format_time(adjusted)}", 4)
        time.sleep(1.2)

        return adjusted, label

    def end_screen(self):
        self.clear()
        self.write_line("  You're all done!  ", 1)
        self.write_line("--------------------", 2)
        self.write_line(" Press any button   ", 3)
        self.write_line("   to restart       ", 4)

        self.wait_for_button()
        return "restart"

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
        self.rotary.close()
