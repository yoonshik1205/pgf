from src.utils import *

# objects

class element(object):
    '''
    base class for game elements, contained within scenes

    ### Attributes:
        `surface`: surface belonging to element, blitted at top left corner by default
        
        `x`, `y`: position
        
        `pos`: vector of `x` and `y`

        `anchor`: the position to anchor the offset from when scaling the parent scene,
        one of "topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright"
        
        `z`: z-index for layering
        
        `w`, `h`: width and height of `surface`

        `parent_scene`: scene that contains element

        `pressed_behavior`: function to call when this element is pressed

        `pressable`: boolean of whether there is a pressed behavior

    ### Methods:
        `get_rect()`: returns `pg.Rect` object with `x`, `y`, `w`, `h` attributes by default

        `blit(screen)`: blits `self.surface` to `screen` at `x`, `y` by default

        `collidepoint(pos)`: returns whether a point in parent scene coordinates is inside the element

        `step(dt)`: called every frame, used for updating element state, only handles presses by default

        `handle_resize()`: called when window is resized, by default it scales the anchor positions and not the offsets

        `process_input(inpt)`: called when user input or events need to be processed

        `collisioncheck(other)`: returns `True` if `self` and `other` are colliding, `False` otherwise (uses `get_rect()` by default)
    '''
    def __init__(self, z:int, surf:pg.Surface, pos, anchor:str='topleft', pressed_behavior=None) -> None:
        assert anchor in ["topleft", "top", "topright", "left", "center", "right", "bottomleft", "bottom", "bottomright"]
        self.anchor = anchor
        _iax = 0 if 'left' in anchor else (scfg.WIDTH if 'right' in anchor else scfg.WIDTH//2)
        _iay = 0 if 'top' in anchor else (scfg.HEIGHT if 'bottom' in anchor else scfg.HEIGHT//2)
        self.init_anchor_pos = vector(_iax, _iay)

        self.surface = surf
        if isinstance(pos, vector): self.pos = pos
        else: self.pos = vector(pos)
        self.anchor_offset = self.pos - self.init_anchor_pos
        self.z = z
        self.w, self.h = surf.get_size()
        self.parent_scene = None
        
        self.pressed = False
        if pressed_behavior == None:
            self.pressed_behavior = lambda: None
            self.pressable = False
        else:
            self.pressed_behavior = pressed_behavior
            self.pressable = True

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
    def collidepoint(self, pos):
        return self.get_rect().collidepoint((pos[0], pos[1]))
    def step(self, dt:float):
        if self.pressable and self.pressed:
            self.pressed = False
            self.pressed_behavior()
    def handle_resize(self):
        iax, iay = self.init_anchor_pos.tuple
        anchor_pos = vector(iax * self.parent_scene.w_scale, iay * self.parent_scene.h_scale)
        self.pos = anchor_pos + self.anchor_offset
    def process_input(self, inpt:pg.event.Event):
        if inpt.type==pg.USEREVENT and inpt.msg=='window_resize':
            self.handle_resize()
        elif self.pressable and inpt.type==pg.MOUSEBUTTONDOWN and inpt.button==1:
            truepos = (inpt.pos[0]/scfg.SCALE_FACTOR-self.parent_scene.true_x,
                        inpt.pos[1]/scfg.SCALE_FACTOR-self.parent_scene.true_y)
            if self.collidepoint(truepos):
                self.pressed = True
    def collisioncheck(self, other:'element'):
        return self.get_rect().colliderect(other.get_rect())
    
class sprite(element):
    '''
    like `element`, but defined with multiple surfaces so it's easier to switch

    if `surf_names` is provided as a list with the same length as `surfs`, then each surface can be set using the names

    `set_surf(idx_or_name)` is called to change the surface
    '''
    def __init__(self, z:int, surfs:list, pos, anchor:str='topleft', surf_names:list=[]) -> None:
        super().__init__(z, surfs[0], pos, anchor)
        self.surfs = surfs
        if len(surf_names)==len(surfs):
            self.surfs_name = {nm:surf for nm, surf in zip(surf_names, surfs)}
    def set_surf(self, idx_or_name:int|str):
        if isinstance(idx_or_name, int):
            self.surface = self.surfs[idx_or_name]
        else:
            self.surface = self.surfs_name[idx_or_name]

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

        `physics_step(dt)`: always call this function every step to update position
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
    def physics_step(self, dt:float):
        self.calculate_a()
        self.pos += self.v*dt + self.a*(dt**2/2)
        self.v += self.a*dt
        for p in self.parent_scene.pushers:
            if p.pushes(self):
                self.pos -= self.v*dt - self.a*(dt**2/2)
                self.v = vector(0, 0)
                self.collided_behavior(p)
                break


class scene(element):
    '''
    base class for scenes, subclass of element
    
    scenes are isolated environments that contain elements

    ### Attributes:
        `elements`: list of elements contained within scene, sorted by z

        `w`, `h`: width and height, gets overridden if custom surface is given

        `bgcolor`: background color

        `pos`: vector of `x` and `y`

        `x`, `y`: position of top left corner

        `surface`: the surface of the scene itself

        `physics`: whether or not physics is enabled

        `pushers`: list of elements that push other elements

    ### Methods:
        `add_element(elem)`: adds `elem` to `self.elements`

        `handle_resize()`: default behavior is to scale the background and position if a root scene and scale position like an element otherwise

        `process_input(inpt)`: for when user input or events need to be processed (empty by default)

        `blit(screen)`: blits

        `step(dt)`: calls `step(dt)` on all elements by default
    '''
    def __init__(self, size:tuple, elems:list, bgcolor, pos=(0,0), z:int=-1, surf:pg.Surface=None, anchor:str='topleft', physics:bool=False) -> None:
        self.elements = elems
        for e in self.elements: e.parent_scene = self
        self.elements.sort(key=lambda x:x.z)

        self.parent_scene = None
        if surf==None:
            self.init_env = pg.Surface(size, pg.SRCALPHA)
            self.init_env.fill(bgcolor)
        else:
            self.init_env = surf
        self.scaled_init_env = self.init_env.convert_alpha()
        super().__init__(z, self.init_env.convert_alpha(), pos, anchor)
        self._w, self._h = self.w, self.h
        self._x, self._y = self.pos.tuple

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

    @property
    def w_scale(self):
        return self.w / self._w
    @property
    def h_scale(self):
        return self.h / self._h
    @property
    def true_x(self):
        if self.parent_scene==None: return self.x
        else: return self.parent_scene.true_x + self.x
    @property
    def true_y(self):
        if self.parent_scene==None: return self.y
        else: return self.parent_scene.true_y + self.y
        
    def add_element(self, elem:element):
        elem.parent_scene = self
        self.elements.append(elem)
        self.elements.sort(key=lambda x:x.z)
        if self.physics and isinstance(elem, collidable) and elem.push_others:
            self.pushers.append(elem)
    def handle_resize(self):
        if self.parent_scene!=None:
            super().handle_resize()
        else:
            _scaled_wh = (self._w * scfg.WINDOW_W_SCALE / scfg.SCALE_FACTOR, self._h * scfg.WINDOW_H_SCALE / scfg.SCALE_FACTOR)
            _scaled_xy = (self._x * scfg.WINDOW_W_SCALE / scfg.SCALE_FACTOR, self._y * scfg.WINDOW_H_SCALE / scfg.SCALE_FACTOR)
            self.scaled_init_env = pg.transform.scale(self.init_env, _scaled_wh)
            self.surface = self.scaled_init_env.convert_alpha()
            self.w, self.h = _scaled_wh
            self.x, self.y = _scaled_xy
        for e in self.elements: e.handle_resize()
    def process_input(self, inpt:pg.event.Event):
        super().process_input(inpt)
        for e in self.elements: e.process_input(inpt)
    def blit(self, screen:pg.Surface):
        self.surface.blit(self.scaled_init_env, (0, 0))
        for e in self.elements: e.blit(self.surface)
        if self.parent_scene==None: screen.blit(pg.transform.scale(self.surface, (self.w*scfg.SCALE_FACTOR, self.h*scfg.SCALE_FACTOR)), (self.x*scfg.SCALE_FACTOR, self.y*scfg.SCALE_FACTOR))
        else: screen.blit(self.surface, (self.x, self.y))
    def step(self, dt:float):
        super().step(dt)
        for e in self.elements: e.step(dt)

class gametemplate(object):
    '''
    base class for the game object, must be inherited only by a single class specifically named `game`

    ### Attributes:
        `curscenes`: list of scenes currently active

    ### Methods:
        `process_input(inpt)`: calls `process_input()` on all active scenes

        `step(dt)`: calls `step(dt)` on all active scenes

        `update_screen(screen)`: blits all active scenes to `screen` and updates display

        `cleanup()`: called when game is closed (empty by default)
    '''
    def __init__(self, screen_ref:pg.Surface) -> None:
        self.curscenes = []
        self.screen_ref = screen_ref
    def process_input(self, inpt:pg.event.Event):
        for s in self.curscenes: s.process_input(inpt)
    def step(self, dt:float):
        for s in self.curscenes: s.step(dt)
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
    def __init__(self, z:int, text:str, align:str, pos:tuple, font, color, size:float=16, anchor:str='topleft', pressed_behavior=None) -> None:
        super().__init__(z, pg.Surface((0, 0)), pos, anchor, pressed_behavior)
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
    def __init__(self, z:int, text:str, align:str, pos:tuple, max_width, font, color, size:float=16, anchor:str='topleft', pressed_behavior=None) -> None:
        self.max_width = max_width
        super().__init__(z, text, align, pos, font, color, size, anchor, pressed_behavior)
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
