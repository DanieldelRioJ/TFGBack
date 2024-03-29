from random import randint
from objects.Appearance import Appearance

class VideoObject(object):
    def __init__(self,
                 id:int,
                 appearances,
                 color=None):
        self.group = None
        if appearances is None:
            appearances = []
        self.id=id
        self.static_points = 0
        self.appearances=appearances
        if(color==None):
            color=(randint(0,255),randint(0,255),randint(0,255))
        self.color=color
        self.portrait=None
        self.average_speed=None
        self.angle=None
        self.upper_colors=None
        self.lower_colors=None