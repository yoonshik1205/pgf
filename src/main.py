from src.objects import *


def main():
    screen = pg.display.set_mode((scfg.TRUE_WIDTH, scfg.TRUE_HEIGHT), pg.RESIZABLE, vsync=1)
    # WINDOW_ICON = generate_surface('screenicon.png', 32, 32)
    # pg.display.set_icon(WINDOW_ICON)
    pg.display.set_caption(WINDOW_TITLE)
    clock = pg.time.Clock()

    load_cfg()

    g = game()
    dt = TICK
    cont = True
    while cont:
        for event in pg.event.get():
            if event.type==pg.QUIT: cont = False
            elif event.type==pg.VIDEORESIZE:
                scfg.TRUE_WIDTH = event.w
                scfg.TRUE_HEIGHT = event.h
                scfg.WIDTH = scfg.TRUE_WIDTH / scfg.SCALE_FACTOR
                scfg.HEIGHT = scfg.TRUE_HEIGHT / scfg.SCALE_FACTOR
                scfg.WINDOW_W_SCALE = event.w / INIT_TRUE_WIDTH
                scfg.WINDOW_H_SCALE = event.h / INIT_TRUE_HEIGHT
                g.process_input(pg.event.Event(pg.USEREVENT, {'msg':'window_resize'}))
            else: g.process_input(event)
        if not cont: break
        g.step(dt)
        g.update_screen(screen)
        dt = clock.tick(TPS) / 1000
    g.cleanup()
    pg.quit()
