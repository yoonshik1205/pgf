import os, sys
from src.main import main

if sys.platform == 'win32':
    import ctypes
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except AttributeError:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError: pass


if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

main()
