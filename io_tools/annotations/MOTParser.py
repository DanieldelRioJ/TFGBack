from objects.Person import Person
from objects.Appearance import Appearance
from helpers import Helper
from objects.Point import Point

class MOTParser():
    def __init__(self, filePath:str):
        self.filePath=filePath

    def parse(self, remove_static_objects=False, iou_limit=0.99, static_porcentage_time=0.99):
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
                    objects[id] = Person(id,[])

                col=int(float(attr[2]))
                dif_col=0
                row=int(float(attr[3]))
                dif_row=0
                if(col<0):
                    dif_col=col
                    col=0
                if(row<0):
                    dif_row=row
                    row=0
                #dif col and dif row is used to reduce the length(w and h) that we add correcting negative coordinates(col and row of upper left corner)
                appearance = Appearance(objects[id], frame, col,
                                        row,
                                        int(float(attr[4]))+dif_col,
                                        int(float(attr[5]))+dif_row,
                                        float(attr[6]))
                objects[id].appearances.append(appearance)
                map.get(frame).append(appearance)

            #If we have to remove static objects, we use Iou
            if remove_static_objects:
                static_elements=[]
                for id in objects:
                    obj=objects[id]
                    last=obj.appearances[0]
                    for appearance in obj.appearances:
                        iou=Helper.get_iou(Point(last.col,last.row),Point(last.col+last.w,last.row+last.w),
                                          Point(appearance.col,appearance.row),Point(appearance.col+appearance.w,appearance.row+appearance.w))
                        last=appearance
                        appearance.iou=iou
                        if iou > iou_limit:
                            appearance.object.static_points+=1
                    if obj.static_points / len(obj.appearances) > static_porcentage_time:
                        static_elements.append(id)

                print(f"Removed elements = {len(static_elements)}")

                for id in static_elements:
                    obj= objects[id]
                    del objects [id]
                    for appearance in obj.appearances:
                        map.get(appearance.frame).remove(appearance)
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
