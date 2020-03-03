from random import randint
from objects.Appearance import Appearance

class Person:
    def __init__(self,
                 id:int,
                 appearances:[Appearance]=[],
                 color=None):
        self.id=id
        self.appearances=appearances
        if(color==None):
            color=(randint(0,255),randint(0,255),randint(0,255))
        self.color=color