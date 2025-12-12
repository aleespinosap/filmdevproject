# ledcontrol.py
from gpiozero import LED, PWMLED
from time import sleep, monotonic, time
import threading

blue = PWMLED(17)
yellow = LED(27)
green = LED(22)

stop_flag = False
green_blink_flag = False
pause_flag = False


def cleanup():
    """Ensure all LED resources are released and threads stop.

    The GPIOZero objects are closed after explicitly stopping any
    background animation loops so that pins are reset even if the
    program exits due to a KeyboardInterrupt.
    """

    leds_off()
    yellow.close()
    green.close()
    blue.close()


def leds_off():
    """Stop any running LED threads and power everything down."""

    global stop_flag, green_blink_flag, pause_flag
    stop_flag = True
    green_blink_flag = False
    pause_flag = False
    yellow.off()
    blue.off()
    green.off()


def rerun_stop_flag():

    global stop_flag
    stop_flag = False


def pause_on():

    global pause_flag
    pause_flag = True


def pause_off():

    global pause_flag
    pause_flag = False


def blue_threading(duration):

    elapsed = 0.0
    step_dt = 0.01

    while elapsed < duration and not stop_flag:

        for i in range(0, 101):
            if stop_flag or elapsed >= duration:
                break


            while pause_flag and not stop_flag:
                blue.off()
                sleep(0.05)
            if stop_flag:
                break

            blue.value = i / 100
            sleep(step_dt)
            elapsed += step_dt
            if elapsed >= duration:
                break


        for i in range(100, -1, -1):
            if stop_flag or elapsed >= duration:
                break

            while pause_flag and not stop_flag:
                blue.off()
                sleep(0.05)
            if stop_flag:
                break

            blue.value = i / 100
            sleep(step_dt)
            elapsed += step_dt
            if elapsed >= duration:
                break

    blue.off()


def blue_cycle(duration):
    rerun_stop_flag()
    t = threading.Thread(target=blue_threading, args=(duration,))
    t.daemon = True
    t.start()
    return t


def yellow_threading(duration):

    elapsed = 0.0
    last = monotonic()

    while elapsed < duration and not stop_flag:
        now = monotonic()

        if pause_flag:
            yellow.off()
            last = now
            sleep(0.05)
            continue

        dt = now - last
        if dt < 0:
            dt = 0
        elapsed += dt
        last = now

        if elapsed >= duration:
            break

        cycle_pos = elapsed % 30.0

        if cycle_pos < 10.0:
            yellow.on()
            sleep(0.5)
            if stop_flag or pause_flag:
                continue
            yellow.off()
            sleep(0.5)
        else:
            yellow.off()
            sleep(0.1)

    yellow.off()


def yellow_cycle(duration):
    rerun_stop_flag()
    t = threading.Thread(target=yellow_threading, args=(duration,))
    t.daemon = True
    t.start()
    return t


def green_cycle():

    global green_blink_flag
    green_blink_flag = False
    green.on()


def green_done():

    global green_blink_flag
    green_blink_flag = False
    green.off()


def green_blink():

    global green_blink_flag
    green_blink_flag = True

    def _blink():
        while green_blink_flag:
            green.on()
            sleep(0.4)
            green.off()
            sleep(0.4)
        green.off()

    t = threading.Thread(target=_blink)
    t.daemon = True
    t.start()
    return t


def green_blink_stop():
    global green_blink_flag
    green_blink_flag = False
    green.off()
