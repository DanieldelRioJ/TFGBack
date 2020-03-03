class Appearance:
    def __init__(self, object, frame, col:int, row:int, w:int, h:int, confidence:float=1):
        self.object=object
        self.frame=frame
        self.col=col
        self.row=row
        self.w=w
        self.h=h
        self.confidence=confidence
