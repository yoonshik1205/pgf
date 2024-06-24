from src.consts import *

pg.display.set_mode((scfg.TRUE_WIDTH, scfg.TRUE_HEIGHT), pg.RESIZABLE, vsync=1)

def generate_surface(imagename: str, w:float, h:float):
    '''
    returns a scaled surface from an image file in the images folder

    ### Parameters:
        `imagename`: name of image file (including extension)

        `w`, `h`: width and height of returned surface
    '''
    im_dir = os.path.join(os.path.dirname(__file__), 'images', imagename)
    img = pg.image.load(im_dir).convert_alpha()
    if w==img.get_width() and h==img.get_height(): return img
    return pg.transform.smoothscale(img, (w, h))

def get_audio(soundname:str):
    '''
    gets audio file from sounds folder

    ### Parameters:
        `soundname`: name of sound file (including extension)
    '''
    return pg.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sounds', soundname))

# level data



# images and sounds


# S_MUSIC = os.path.join(os.path.dirname(__file__), 'sounds', 'music.mp3')



