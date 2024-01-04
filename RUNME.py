import os, sys
from src.main import main

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

main()
