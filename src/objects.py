from src.templates import *

# game objects



# default objects

class esc_menu(scene):
    def __init__(self):
        bgcolor = (0, 0, 0)
        textcolor = (255, 255, 255)
        fontname = 'Arial'
        self.scaletext = text(1, 'Scale: 1x', 'center', (100, 100), fontname, textcolor)
        self.scales = [0.5, 0.75, 1., 1.25, 1.5, 2.]
        self.scales_display = ['0.5', '0.75', '1', '1.25', '1.5', '2']
        self.scale_idx = 3
        self.update_scale(scfg.SCALE_FACTOR)
        elems = [
            text(1, 'PAUSED', 'center', (100, 40), fontname, textcolor, 24),
            self.scaletext,
            text(1, ' < ', 'center', (30, 100), fontname, textcolor, pressed_behavior=lambda: post_event('scaling_down')),
            text(1, ' > ', 'center', (170, 100), fontname, textcolor, pressed_behavior=lambda: post_event('scaling_up')),
            text(1, 'Toggle Fullscreen', 'center', (100, 150), fontname, textcolor, pressed_behavior=toggle_fullscreen),
            text(1, 'Quit Game', 'center', (100, 200), fontname, textcolor, pressed_behavior=quitgame)
        ]
        self.menu = scene((200, 400), elems, bgcolor, (init_scfg.WIDTH//2-100, init_scfg.HEIGHT//2-200), anchor='center')
        super().__init__((init_scfg.WIDTH, init_scfg.HEIGHT), [self.menu], (0, 0, 0))
    def update_scale(self, new_scale:float):
        if new_scale < self.scales[0] or new_scale > self.scales[-1]: return
        closest_idx = 3
        closest_dist = float('inf')
        for i, sc in enumerate(self.scales):
            if abs(new_scale-sc) < closest_dist:
                closest_idx = i
                closest_dist = abs(new_scale-sc)
        self.scale_idx = closest_idx
        scfg.SCALE_FACTOR = self.scales[self.scale_idx]
        self.scaletext.updatetext(f'Scale: {self.scales_display[self.scale_idx]}x')
        post_event('window_resize')
    def update_scale_idx(self, new_scale_idx:int):
        if new_scale_idx < 0 or new_scale_idx >= len(self.scales): return
        self.scale_idx = new_scale_idx
        scfg.SCALE_FACTOR = self.scales[self.scale_idx]
        self.scaletext.updatetext(f'Scale: {self.scales_display[self.scale_idx]}x')
        post_event('window_resize')
    def process_input(self, inpt: pg.event.Event):
        if inpt.type==pg.KEYDOWN and inpt.key==pg.K_ESCAPE:
            post_event('exit_esc_menu')
        elif inpt.type==pg.USEREVENT and inpt.msg=='scaling_down':
            self.update_scale_idx(self.scale_idx - 1)
        elif inpt.type==pg.USEREVENT and inpt.msg=='scaling_up':
            self.update_scale_idx(self.scale_idx + 1)
        else: super().process_input(inpt)

class game(gametemplate):
    def __init__(self, screen_ref:pg.Surface) -> None:
        super().__init__(screen_ref)
        
        self.esc = esc_menu()
        # declare scenes here
        self.s0 = scene((init_scfg.WIDTH, init_scfg.HEIGHT), [], (127,127,127))


        self.curscenes = [self.s0]

        self.temp_curscenes = []
        self.paused = False

        # pg.mixer.music.load(S_MUSIC)
        # pg.mixer.music.set_volume(0.5)
        # pg.mixer.music.play(-1)
        
    def process_input(self, inpt: pg.event.Event):
        super().process_input(inpt)
        if not self.paused and inpt.type==pg.KEYDOWN and inpt.key==pg.K_ESCAPE:
            self.temp_curscenes = self.curscenes
            self.esc.init_env = pg.transform.smoothscale(self.screen_ref, (INIT_TRUE_WIDTH, INIT_TRUE_HEIGHT))
            self.curscenes = [self.esc]
            post_event('window_resize')
            self.paused = True
        elif inpt.type==pg.USEREVENT:
            if self.paused and inpt.msg=='exit_esc_menu':
                self.curscenes = self.temp_curscenes
                self.paused = False
            # deal with input events that are labeled, ex)
            # if inpt.msg=='startgame':
            #     self.curscenes = [self.s1]
            pass

