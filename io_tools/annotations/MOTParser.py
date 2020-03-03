from objects.Person import Person
from objects.Appearance import Appearance

class MOTParser():
    def __init__(self, filePath:str):
        self.filePath=filePath

    def parse(self):
        map = {}
        objects = {}
        with open(self.filePath, "r") as file:
            lines = file.readlines()

            for line in lines:
                attr = line.split(",")
                id = int(attr[1])
                frame=int(attr[0])
                if (map.get(frame) == None):
                    map[frame] = []
                if objects.get(id) == None:
                    objects[id] = Person(id)
                appearance = Appearance(objects[id], frame, int(float(attr[2])),
                                        int(float(attr[3])),
                                        int(float(attr[4])),
                                        int(float(attr[5])),
                                        float(attr[6]))
                objects[id].appearances.append(appearance)
                map.get(frame).append(appearance)
            return objects, map

    """def parse(self):
        map={}
        objects={}
        with open(self.filePath,"r") as file:
            lines=file.readlines()
            objects_of_frame=[]

            frame=1
            for line in lines:
                attr=line.split(",")
                id=int(attr[1])
                # Si nuevo frame
                if(frame<int(attr[0])):
                    map[frame]=objects_of_frame
                    objects_of_frame=[]
                    frame+=1
                if objects.get(id)==None:
                    objects[id]=Person(id)
                appearance=Appearance(objects[id],frame,int(float(attr[2])),
                                               int(float(attr[3])),
                                               int(float(attr[4])),
                                               int(float(attr[5])),
                                               float(attr[6]))
                objects[id].appearances.append(appearance)
                objects_of_frame.append(appearance)
            map[frame]=objects_of_frame
            return objects,map"""
