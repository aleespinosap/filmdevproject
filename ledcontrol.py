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
    """Reset the stop flag to allow LED animation threads to resume."""

    global stop_flag
    stop_flag = False


def pause_on():
    """Pause all running LED animations while preserving their state."""

    global pause_flag
    pause_flag = True


def pause_off():
    """Resume all paused LED animations."""

    global pause_flag
    pause_flag = False


def blue_threading(duration):
    """Worker thread that fades the blue LED smoothly in and out for a specified duration.

    Implements a breathing animation with pause and stop signal support.
    Used internally by blue_cycle(); do not call directly.

    Args:
        duration (float): How long to animate in seconds.
    """

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
    """Start a smooth breathing animation on the blue LED (active/current stage indicator).

    Creates a daemon thread that fades the LED in and out continuously.
    Respects pause and stop signals from the main thread.

    Args:
        duration (float): How long to animate in seconds.

    Returns:
        threading.Thread: The animation thread (daemon).
    """
    rerun_stop_flag()
    t = threading.Thread(target=blue_threading, args=(duration,))
    t.daemon = True
    t.start()
    return t


def yellow_threading(duration):
    """Worker thread that blinks the yellow LED for a specified duration.

    Implements a 30-second cycle with 10 seconds of blinking followed by
    20 seconds off. Respects pause and stop signals. Used internally by
    yellow_cycle(); do not call directly.

    Args:
        duration (float): How long to animate in seconds.
    """

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
    """Start a blinking pattern on the yellow LED (warning/caution indicator).

    Creates a daemon thread that blinks in 30-second cycles (10s on, 20s off).
    Respects pause and stop signals from the main thread.

    Args:
        duration (float): How long to animate in seconds.

    Returns:
        threading.Thread: The animation thread (daemon).
    """
    rerun_stop_flag()
    t = threading.Thread(target=yellow_threading, args=(duration,))
    t.daemon = True
    t.start()
    return t


def green_cycle():
    """Light the green LED steadily to indicate stage is active/ready.

    Stops any blinking animation and sets the LED to solid on.
    """

    global green_blink_flag
    green_blink_flag = False
    green.on()


def green_done():
    """Turn off the green LED to indicate stage completion.

    Stops any blinking animation and powers off the LED.
    """

    global green_blink_flag
    green_blink_flag = False
    green.off()


def green_blink():
    """Start a steady blinking pattern on the green LED (ready/completion indicator).

    Creates a daemon thread that blinks the LED at 0.4-second intervals.
    The blink continues until green_blink_stop() is called.

    Returns:
        threading.Thread: The blinking animation thread (daemon).
    """

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
    """Stop the green LED blinking and turn it off.

    Halts any active blinking animation and powers off the LED.
    """
    global green_blink_flag
    green_blink_flag = False
    green.off()
