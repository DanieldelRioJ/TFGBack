import math
import numpy as np

def do_filter(object_dict, path_filter):
    if path_filter is None:
        return object_dict

    erratic=path_filter.get('erratic')
    new_object_list = {}

    #If we want to see objects with erratic movement
    if erratic:
        for obj_id in object_dict:
            obj=object_dict.get(obj_id)
            if obj.angle is None:
                new_object_list[obj_id]=obj
        return new_object_list

    #If we want to see objects with a specific direction
    direction_params=[path_filter.get('right'),path_filter.get('down_right'),
        path_filter.get('down'),path_filter.get('down_left'),path_filter.get('left'),
        path_filter.get('up_left'),path_filter.get('up'),path_filter.get('up_right')]

    #
    if all(dir==0 for dir in direction_params):
        return object_dict

    # Just check the direction
    for i, dir in enumerate(direction_params):
        if not dir:
            continue
        min_angle = (i * 45 - 35)%360
        max_angle = (i * 45 + 35)%360

        if min_angle<max_angle: #Remember, its a circle, min can be 350º and max 20º for example.
            for id, obj in object_dict.items():
                if obj.angle == None:
                    continue
                obj_angle_degrees = math.degrees(obj.angle)
                if (obj_angle_degrees >= min_angle and obj_angle_degrees <= max_angle):
                    # dir_obj_list.append(obj)
                    new_object_list[id] = obj
        else:
            for id, obj in object_dict.items():
                if obj.angle == None:
                    continue
                obj_angle_degrees = math.degrees(obj.angle)
                if (obj_angle_degrees >= min_angle or obj_angle_degrees <= max_angle):
                    # dir_obj_list.append(obj)
                    new_object_list[id] = obj



    return new_object_list