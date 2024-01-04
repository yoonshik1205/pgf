import pygame as pg

from src.utils import *
from src.consts import *
from src.assets import *
from src.templates import *

pg.mixer.pre_init(channels=8)
pg.init()

# game objects



class game(gametemplate):
    def __init__(self) -> None:
        super().__init__()
        self.s0 = None
        # declare scenes here

        self.curscenes = [self.s0]
        # pg.mixer.music.load(S_MUSIC)
        # pg.mixer.music.set_volume(0.5)
        # pg.mixer.music.play(-1)
        
    def process_input(self, inpt: pg.event.Event):
        super().process_input(inpt)
        if inpt.type==pg.USEREVENT:
            # deal with input events that are labeled, ex)
            # if inpt.msg=='startgame':
            #     self.curscenes = [self.s1]
            pass

