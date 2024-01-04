import pygame as pg
import os

from src.consts import *
from src.utils import *

pg.init()

# objects

class element(object):
    '''
    base class for game elements, contained within scenes

    ### Attributes:
        `surface`: surface belonging to element, blitted at top left corner by default
        
        `x`, `y`: position
        
        `pos`: vector of `x` and `y`
        
        `z`: z-index for layering
        
        `w`, `h`: width and height of `surface`

        `parent_scene`: scene that contains element

    ### Methods:
        `get_rect()`: returns `pg.Rect` object with `x`, `y`, `w`, `h` attributes by default

        `blit(screen)`: blits `self.surface` to `screen` at `x`, `y` by default

        `step()`: called every frame, used for updating element state (empty by default)

        `process_input(inpt)`: called when user input or events need to be processed (empty by default)

        `collisioncheck(other)`: returns `True` if `self` and `other` are colliding, `False` otherwise (uses `get_rect()` by default)
    '''
    def __init__(self, z:int, surf:pg.Surface, pos) -> None:
        self.surface = surf
        if isinstance(pos, vector): self.pos = pos
        else: self.pos = vector(pos)
        self.z = z
        self.w, self.h = surf.get_size()
        self.parent_scene = None
    @property
    def x(self):
        return self.pos.x
    @x.setter
    def x(self, val):
        self.pos.x = val
    @property
    def y(self):
        return self.pos.y
    @y.setter
    def y(self, val):
        self.pos.y = val

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.w, self.h)
    def blit(self, screen:pg.Surface):
        screen.blit(self.surface, (self.x, self.y))
    def step(self):
        pass
    def process_input(self, inpt:pg.event.Event):
        pass
    def collisioncheck(self, other:'element'):
        return self.get_rect().colliderect(other.get_rect())

class collidable(object):
    '''
    template for collidable objects (always inherit alongside a class based on `element`)

    ### Attributes:
        `push_others`: whether or not this element causes other elements to move when colliding with them

    ### Methods:
        `pushes(other)`: returns `True` if `self` is pushing `other`, `False` otherwise (uses `collisioncheck()` by default)
    '''
    def __init__(self, push_others:bool=False) -> None:
        self.push_others = push_others
    def pushes(self, other:'collidable'):
        if self is other: return False
        if not self.push_others: return False
        return self.collisioncheck(other)

class physicsobject(collidable):
    '''
    template for physics objects (subclass of `collidable`)

    ### Attributes:
        `v`: velocity
        
        `a`: acceleration
        
        `mass`: mass

    ### Methods:
        `calculate_a()`: calculates acceleration (empty by default)

        `collided_behavior(other)`: called when `self` collides with `other` (empty by default)

        `physics_step()`: always call this function every step to update position
    '''
    def __init__(self, mass:float=1, v_init=(0,0), push_others:bool=False) -> None:
        super().__init__(push_others)
        if isinstance(v_init, vector): self.v = v_init
        else: self.v = vector(v_init)
        self.a = vector(0, 0)
        if mass==0: raise ValueError("mass cannot be 0")
        self.mass = mass
    def calculate_a(self):
        pass
    def collided_behavior(self, other:collidable):
        pass
    def physics_step(self):
        self.calculate_a()
        self.pos += self.v*TICK + self.a*(TICK**2/2)
        self.v += self.a*TICK
        for p in self.parent_scene.pushers:
            if p.pushes(self):
                self.pos -= self.v*TICK - self.a*(TICK**2/2)
                self.v = vector(0, 0)
                self.collided_behavior(p)
                break

class button(element):
    '''
    base class for buttons

    ### Attributes:
        `pressed`: whether or not button is pressed

    ### Methods:
        `collidepoint(pos)`: returns `True` if `pos` is within `self.get_rect()`, `False` otherwise

        `pressed_behavior()`: called when button is pressed (by default, sets `self.pressed` to `False`)
    '''
    def __init__(self, z: int, surf: pg.Surface, pos) -> None:
        super().__init__(z, surf, pos)
        self.pressed = False
    def collidepoint(self, pos):
        return self.get_rect().collidepoint((pos[0], pos[1]))
    def process_input(self, inpt: pg.event.Event):
        if inpt.type==pg.MOUSEBUTTONDOWN and inpt.button==1:
            truepos = (inpt.pos[0]/TRUE_WIDTH*WIDTH-self.parent_scene.x, inpt.pos[1]/TRUE_HEIGHT*HEIGHT-self.parent_scene.y)
            if self.collidepoint(truepos):
                self.pressed = True
        elif inpt.type==pg.MOUSEBUTTONUP and inpt.button==1:
            self.pressed = False
    def pressed_behavior(self):
        self.pressed = False
    def step(self):
        if self.pressed: self.pressed_behavior()

class scene(object):
    '''
    base class for scenes
    
    scenes are isolated environments that contain elements

    ### Attributes:
        `elements`: list of elements contained within scene, sorted by z

        `size`: tuple of width and height

        `bgcolor`: background color

        `pos`: vector of `x` and `y`

        `x`, `y`: position of top left corner

        `env`: the surface of the scene itself

        `physics`: whether or not physics is enabled

        `pushers`: list of elements that push other elements

    ### Methods:
        `add_element(elem)`: adds `elem` to `self.elements`

        `process_input(inpt)`: for when user input or events need to be processed (empty by default)

        `blit(screen)`: blits

        `step()`: calls `step()` on all elements by default
    '''
    def __init__(self, size:tuple, elems:list, bgcolor, pos=(0,0), physics:bool=False) -> None:
        self.elements = elems
        for e in self.elements: e.parent_scene = self
        self.elements.sort(key=lambda x:x.z)
        self.size = size
        self.bgcolor = bgcolor
        if isinstance(pos, vector): self.pos = pos
        else: self.pos = vector(pos)
        self.env = pg.Surface(size, pg.SRCALPHA)
        self.physics = physics
        self.pushers = []
        if physics:
            for e in self.elements:
                if isinstance(e, collidable) and e.push_others:
                    self.pushers.append(e)
    @property
    def x(self):
        return self.pos.x
    @x.setter
    def x(self, val):
        self.pos.x = val
    @property
    def y(self):
        return self.pos.y
    @y.setter
    def y(self, val):
        self.pos.y = val
        
    def add_element(self, elem:element):
        elem.parent_scene = self
        self.elements.append(elem)
        self.elements.sort(key=lambda x:x.z)
        if self.physics and isinstance(elem, collidable) and elem.push_others:
            self.pushers.append(elem)
    def process_input(self, inpt:pg.event.Event):
        for e in self.elements: e.process_input(inpt)
    def blit(self, screen:pg.Surface):
        self.env.fill(self.bgcolor)
        for e in self.elements: e.blit(self.env)
        screen.blit(pg.transform.scale(self.env, (self.size[0]/WIDTH*TRUE_WIDTH, self.size[1]/HEIGHT*TRUE_HEIGHT)), (self.x/WIDTH*TRUE_WIDTH, self.y/HEIGHT*TRUE_HEIGHT))
    def step(self):
        for e in self.elements: e.step()

class gametemplate(object):
    '''
    base class for the game object, must be inherited only by a single class specifically named `game`

    ### Attributes:
        `curscenes`: list of scenes currently active

    ### Methods:
        `process_input(inpt)`: calls `process_input()` on all active scenes

        `step()`: calls `step()` on all active scenes

        `update_screen(screen)`: blits all active scenes to `screen` and updates display

        `cleanup()`: called when game is closed (empty by default)
    '''
    def __init__(self) -> None:
        self.curscenes = []
    def process_input(self, inpt:pg.event.Event):
        for s in self.curscenes: s.process_input(inpt)
    def step(self):
        for s in self.curscenes: s.step()
    def update_screen(self, screen:pg.Surface):
        for s in self.curscenes: s.blit(screen)
        pg.display.flip()
    def cleanup(self):
        pass

class text(element):
    '''
    text box class, because pygame does not support multline text

    subclass of `element`, not meant to be inherited but can be

    ### Attributes:
        `surface`: surface of element

        `text`: text of textbox (updating this does NOT update the text, use `updatetext()` instead)

        `z`: z-index for layering

        `alignment`: alignment of text, can be 'left', 'center', or 'right'

        `font`: either the name of the font (fonts directory is searched first, then sysfont) or a `pg.font.Font` object

        `color`: color of text, can be `str` or `tuple`

        `size`: size of text, overridden if `font` is a `pg.font.Font` object

        `x`, `y`: position of top left corner

        `pos`: (`x`, `y`)

        `w`, `h`: width and height of `surface`

    ### Methods:
        `updatetext(text)`: sets the text to be displayed

        `get_rect()`: returns `pg.Rect` object where `self.surface` should be

        `blit(screen)`: blitted according to text alignment: 'left' is top left corner, 'center' is center, 'right' is top right corner
    '''
    def __init__(self, z:int, text:str, align:str, pos:tuple, font, color, size:float=16) -> None:
        super().__init__(z, pg.Surface((0, 0)), pos)
        assert align in {'left', 'center', 'right'}, "incorrect text alignment"
        self.alignment = align
        if isinstance(font, str):
            try:
                fontdir = os.path.join(os.path.dirname(__file__), 'fonts')
                self.font = pg.font.Font(os.path.join(fontdir, font+'.ttf'), size)
            except FileNotFoundError:
                self.font = pg.font.SysFont(font, size)
        else:
            self.font = font
        self.color = color
        self.updatetext(text)
    def updatetext(self, text:str):
        self.text = text
        m = 0.
        lns = []
        for l in text.split('\n'):
            r = self.font.render(l, True, self.color)
            if m<r.get_width(): m=r.get_width()
            lns.append(r)
        self.surface = pg.Surface((m, self.font.get_linesize()*len(lns)), pg.SRCALPHA)
        self.w, self.h = self.surface.get_size()
        for i in range(len(lns)):
            if self.alignment=='left': self.surface.blit(lns[i], (0, i*self.font.get_linesize()))
            elif self.alignment=='center': self.surface.blit(lns[i], (m/2-lns[i].get_width()/2, i*self.font.get_linesize()))
            else: self.surface.blit(lns[i], (m-lns[i].get_width(), i*self.font.get_linesize()))
    def get_rect(self):
        newx = {'left': 0, 'center': self.surface.get_width()/2, 'right': self.surface.get_width()}
        return pg.Rect(self.x-newx[self.alignment], self.y, self.w, self.h)
    def blit(self, screen:pg.Surface):
        newx = {'left': 0, 'center': self.surface.get_width()/2, 'right': self.surface.get_width()}
        screen.blit(self.surface, (self.x-newx[self.alignment], self.y))

class forced_multiline_text(text):
    '''
    text box class that does line wrapping

    despite the description of the text class, this inherits the text class

    ### Attributes:
        `surface`: surface of element

        `text`: text of textbox (updating this does NOT update the text, use `updatetext()` instead)

        `z`: z-index for layering

        `alignment`: alignment of text, can be 'left', 'center', or 'right'

        `font`: either the name of the font (fonts directory is searched first, then sysfont) or a `pg.font.Font` object

        `color`: color of text, can be `str` or `tuple`

        `size`: size of text, overridden if `font` is a `pg.font.Font` object

        `x`, `y`: position of top left corner

        `pos`: (`x`, `y`)

        `w`, `h`: width and height of `surface`

        `max_width`: maximum width of text box in in-game pixels

    ### Methods:
        `updatetext(text)`: sets the text to be displayed

        `get_rect()`: returns `pg.Rect` object where `self.surface` should be

        `blit(screen)`: blitted according to text alignment: 'left' is top left corner, 'center' is center, 'right' is top right corner
    '''
    def __init__(self, z:int, text:str, align:str, pos:tuple, max_width, font, color, size:float=16) -> None:
        self.max_width = max_width
        super().__init__(z, text, align, pos, font, color, size)
    def updatetext(self, text: str):
        ls = []
        for l in text.split('\n'):
            ls.append(l)
            while self.font.size(ls[-1])[0]>self.max_width:
                t_l = ls[-1]
                ls[-1] = ''
                ws = t_l.split(' ')
                for i in range(len(ws)):
                    if self.font.size(ls[-1]+ws[i])[0]<=self.max_width:
                        ls[-1] += ws[i]+' '
                    else:
                        ls[-1] = ls[-1].rstrip()
                        ls.append(' '.join(ws[i:]))
                        break
        newtext = ''
        for l in ls:
            newtext += l+'\n'
        super().updatetext(newtext)
