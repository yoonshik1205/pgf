import pygame as pg

pg.init()

import numpy as np

def xy_to_theta(x:float, y:float) -> float:
    '''
    converts (x, y) vector to direction in radians
    '''
    if x==0 and y==0: return 0
    return np.arctan2(y, x)

def theta_to_xy(theta:float, scale:float=1) -> tuple[float,float]:
    '''
    converts direction in radians to (x, y) vector of length `scale`(default 1)
    '''
    return (np.cos(theta)*scale, np.sin(theta)*scale)

def theta_within_range(theta:float):
    '''
    converts `theta` to a value between 0 and 2pi
    '''
    if theta < 0:
        false_rounds = (-theta)//(2*np.pi)+1
        theta += false_rounds*2*np.pi
    if theta >= 2*np.pi:
        theta %= 2*np.pi
    return theta

def dist(p1, p2):
    '''
    returns distance between two points given in tuple or vector form
    '''
    return np.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

class vector(object):
    '''
    2d vector, supports operations

    ### Attributes:
        `x`, `y`: x and y components

        `theta`: direction in radians

        `magnitude`: magnitude of vector
    '''
    def __init__(self, arg1, arg2:float=1, polar:bool=False) -> None:
        if isinstance(arg1, tuple):
            if len(arg1)!=2: raise ValueError('tuple must have length 2')
            self.x, self.y = arg1
        elif polar:
            self.x, self.y = theta_to_xy(arg1, arg2)
        else:
            self.x, self.y = arg1, arg2
    @property
    def theta(self):
        return xy_to_theta(self.x, self.y)
    @property
    def magnitude(self):
        return dist((0,0), (self.x, self.y))
    @theta.setter
    def theta(self, theta:float):
        self.x, self.y = theta_to_xy(theta, self.magnitude)
    @magnitude.setter
    def magnitude(self, mag:float):
        self.x, self.y = theta_to_xy(self.theta, mag)
    @property
    def tuple(self):
        return (self.x, self.y)
    
    def __add__(self, other:'vector'):
        return vector(self.x+other.x, self.y+other.y)
    def __sub__(self, other:'vector'):
        return vector(self.x-other.x, self.y-other.y)
    def __mul__(self, other:float):
        return vector(self.x*other, self.y*other)
    __rmul__ = __mul__
    def __truediv__(self, other:float):
        return vector(self.x/other, self.y/other)
    def __iadd__(self, other:'vector'):
        self.x += other.x
        self.y += other.y
        return self
    def __isub__(self, other:'vector'):
        self.x -= other.x
        self.y -= other.y
        return self
    def __imul__(self, other:float):
        self.x *= other
        self.y *= other
        return self
    def __itruediv__(self, other:float):
        self.x /= other
        self.y /= other
        return self
    def __getitem__(self, key):
        if key==0: return self.x
        elif key==1: return self.y
        else: raise IndexError('vector index out of range')
    def __copy__(self):
        return vector(self.x, self.y)
    def rotate(self, theta:float):
        self.x, self.y = theta_to_xy(self.theta+theta, self.magnitude)


def post_event(msg:str, data:dict={}):
    '''
    This function is used to post custom events to the event queue, to be processed by all active scenes.

    The event will have the property `msg` set to `msg` and will have all key-value pairs in `data` added to it.
    '''
    payload = {'msg':msg}
    payload.update(data)
    pg.event.post(pg.event.Event(pg.USEREVENT, payload))


# custom util functions
