import os
import math
import pickle
import pygame as pg

pg.mixer.pre_init(channels=8)
pg.init()

# necessary constants

WINDOW_TITLE = 'Game'

INIT_TRUE_WIDTH = 900
INIT_TRUE_HEIGHT = 600

class settings(object):
    def __init__(self):
        # window size in terms of actual pixels
        self.TRUE_WIDTH = INIT_TRUE_WIDTH
        self.TRUE_HEIGHT = INIT_TRUE_HEIGHT

        # window size in terms of in-game pixels
        self.SCALE_FACTOR = 1.
        self.WIDTH = self.TRUE_WIDTH / self.SCALE_FACTOR
        self.HEIGHT = self.TRUE_HEIGHT / self.SCALE_FACTOR

        # how much the window size changed from the initial value
        self.WINDOW_W_SCALE = 1.
        self.WINDOW_H_SCALE = 1.

        self.cfg = {}

scfg = settings()

TPS = 60
TICK = 1/TPS

GAME_DIR = '' # save folder name inside documents


# custom constants
