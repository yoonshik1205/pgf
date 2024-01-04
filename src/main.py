import pygame as pg

from src.consts import *
from src.assets import *
from src.objects import game

pg.init()

def main():
    pg.mixer.pre_init(channels=8)
    pg.init()

    screen = pg.display.set_mode((TRUE_WIDTH, TRUE_HEIGHT))
    # WINDOW_ICON = generate_surface('screenicon.png', 32, 32)
    # pg.display.set_icon(WINDOW_ICON)
    pg.display.set_caption(WINDOW_TITLE)
    clock = pg.time.Clock()

    g = game()
    cont = True
    while cont:
        for event in pg.event.get():
            if event.type==pg.QUIT: cont = False
            else: g.process_input(event)
        if not cont: break
        g.step()
        g.update_screen(screen)
        clock.tick(TPS)
    g.cleanup()
    pg.quit()
