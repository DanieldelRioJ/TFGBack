from objects.VideoObject import Person
from objects.Appearance import Appearance
from helpers import Helper
from objects.Point import Point
from utils.Constants import IOU_LIMIT,IOU_PORCENTAGE

class MOTParser():
    def __init__(self, filePath:str):
        self.filePath=filePath

    #Used for raw input (without beeing preprocessed)
    def __raw_parser__(self,lines,remove_static_objects,iou_limit,static_porcentage_time):
        map = {}
        objects = {}
        for line in lines:
            if line[0] == "#":  # Comentario
                continue
            attr = line.split(",")
            id = int(attr[1])
            frame = int(attr[0])
            if (map.get(frame) == None):
                map[frame] = []
            if objects.get(id) == None:
                objects[id] = Person(id, [])

            col = int(float(attr[2]))
            dif_col = 0
            row = int(float(attr[3]))
            dif_row = 0
            if (col < 0):
                dif_col = col
                col = 0
            if (row < 0):
                dif_row = row
                row = 0
            # dif col and dif row is used to reduce the length(w and h) that we add correcting negative coordinates(col and row of upper left corner)
            appearance = Appearance(objects[id], frame, col,
                                    row,
                                    int(float(attr[4])) + dif_col,
                                    int(float(attr[5])) + dif_row,
                                    float(attr[6]))
            objects[id].appearances.append(appearance)
            map.get(frame).append(appearance)



        # If we have to remove static objects, we use Iou
        if remove_static_objects:
            static_elements = []
            for id in objects:
                obj = objects[id]
                last = obj.appearances[0]
                for appearance in obj.appearances:
                    iou = Helper.get_iou(Point(last.col, last.row), Point(last.col + last.w, last.row + last.w),
                                         Point(appearance.col, appearance.row),
                                         Point(appearance.col + appearance.w, appearance.row + appearance.w))
                    last = appearance
                    appearance.iou = iou
                    if iou > iou_limit:
                        appearance.object.static_points += 1
                if obj.static_points / len(obj.appearances) >= static_porcentage_time:
                    static_elements.append(id)

            print(f"Removed elements = {len(static_elements)}")

            for id in static_elements:
                obj = objects[id]
                del objects[id]
                for appearance in obj.appearances:
                    map.get(appearance.frame).remove(appearance)
        return objects, map

    def __advanced_parser__(self,lines):
        map = {}
        objects = {}
        i=0
        for line in lines:
            if line[0] == "#":  # Comentario
                continue
            if line[0] == ":":  # Fin bloque apariciones
                break
            attr = line.replace('\n','').split(",")
            id = int(attr[1])
            frame = int(attr[0])
            if (map.get(frame) == None):
                map[frame] = []
            if objects.get(id) == None:
                objects[id] = Person(id, [])

            col = int(float(attr[2]))
            dif_col = 0
            row = int(float(attr[3]))
            dif_row = 0
            if (col < 0):
                dif_col = col
                col = 0
            if (row < 0):
                dif_row = row
                row = 0

            speed=attr[11]
            if speed=="None":
                speed=None
            else:
                speed=float(speed)
            # dif col and dif row is used to reduce the length(w and h) that we add correcting negative coordinates(col and row of upper left corner)
            appearance = Appearance(objects[id], frame, col,
                                    row,
                                    int(float(attr[4])) + dif_col,
                                    int(float(attr[5])) + dif_row,
                                    float(attr[6]),
                                    int(float(attr[9])),
                                    int(float(attr[10])),
                                    speed
                                    )
            objects[id].appearances.append(appearance)
            map.get(frame).append(appearance)
            i+=1
        for line in lines[i+2:]:
            if line[0] == "#":  # Comentario
                continue
            attr=line.replace('\n','').split(",")
            id=int(attr[0])
            objects[id].portrait = attr[1]
            if attr[2]!='None':
                objects[id].average_speed=float(attr[2])
            objects[id].first_appearance=objects[id].appearances[0].frame
            objects[id].last_appearance = objects[id].appearances[-1].frame
            if attr[3]!="None":
                objects[id].angle=float(attr[3])
        return objects,map

    def parse(self, remove_static_objects=False, iou_limit=IOU_LIMIT, static_porcentage_time=IOU_PORCENTAGE):

        with open(self.filePath, "r") as file:
            lines = file.readlines()

            if len(lines[0].split(","))<12:
                objects,map=self.__raw_parser__(lines,remove_static_objects,iou_limit,static_porcentage_time)
            else:
                objects, map = self.__advanced_parser__(lines)
        return objects, map

def parseBack(frame_map, object_dict):
    str=[]
    str.append("#{frame_number},{appearance.object.id},{appearance.col},{appearance.row},{appearance.w},{appearance.h},{appearance.confidence},1,1,{appearance.center_col},{appearance.center_row},{appearance.speed}\n")
    for frame_number in frame_map:
        frame_appearances=frame_map.get(frame_number)
        for appearance in frame_appearances:
            str.append(f"{frame_number},{appearance.object.id},{appearance.col},{appearance.row},{appearance.w},{appearance.h},{appearance.confidence},1,1,{appearance.center_col},{appearance.center_row},{appearance.speed}\n")

    str.append(":\n")
    str.append("#{object.id},{object.portrait},{object.average_speed},{object.direction}\n")
    for obj_id in object_dict:
        obj=object_dict[obj_id]
        str.append(f"{obj.id},{obj.portrait},{obj.average_speed},{obj.angle}\n")
    return str
