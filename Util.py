import time
import os
import sys

def formatTime(t):
    return time.strftime('%H:%M:%S', time.gmtime(t))

def formatTimeHM(t):
    return time.strftime('%H:%M', time.gmtime(t))

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

UI_DIR = resource_path("UI Files/")
