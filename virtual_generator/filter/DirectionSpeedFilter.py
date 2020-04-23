import math
import numpy as np

#Filter obj
def __do_filter_speed__(obj_list,speed_filter):
    speed_filter=[speed_filter.get("very_slow"),speed_filter.get("slow"),speed_filter.get("normal"),
                  speed_filter.get("fast"),speed_filter.get("very_fast")]
    if speed_filter is None or all(speed==0 for speed in speed_filter):
        return obj_list

    speed_lists=[obj.average_speed for obj in obj_list]
    mean = np.mean(speed_lists)
    std=np.std(speed_lists)


    aux_list=[]
    #Very slow is <=-1.5std, slow is >-1.5std and <-0.5std
    #Normal is >=-0.5std and <=0.5std
    #Fast is >0.5std and <1.5std, very fast is >=1.5std
    for obj in obj_list:
        desviation=obj.average_speed-mean
        if desviation<=-1.5*std and speed_filter[0]:
            aux_list.append(obj)
        elif desviation>-1.5*std and desviation<-0.5*std and speed_filter[1]:
            aux_list.append(obj)
        elif desviation>=-0.5*std and desviation<=0.5*std and speed_filter[2]:
            aux_list.append(obj)
        elif desviation>0.5*std and desviation<1.5*std and speed_filter[3]:
            aux_list.append(obj)
        elif desviation>=1.5*std and speed_filter[4]:
            aux_list.append(obj)
    return aux_list

def do_filter(object_list, path_filter,speed_filter):
    erratic=path_filter.get('erratic')
    new_object_list = {}

    #If we want to see objects with erratic movement
    if erratic:
        for obj_id in object_list:
            obj=object_list.get(obj_id)
            if obj.angle is None:
                new_object_list[obj_id]=obj
        return new_object_list

    #If we want to see objects with a specific direction
    direction_params=[path_filter.get('right'),path_filter.get('down_right'),
        path_filter.get('down'),path_filter.get('down_left'),path_filter.get('left'),
        path_filter.get('up_left'),path_filter.get('up'),path_filter.get('up_right')]

    #
    if all(dir==0 for dir in direction_params):
        return object_list

    # Just check the direction
    for i, dir in enumerate(direction_params):
        if not dir:
            continue
        min_angle = i * 45 - 35
        max_angle = i * 45 + 35

        dir_obj_list=[]
        for obj_id in object_list:
            obj = object_list.get(obj_id)
            if obj.angle == None:
                continue
            obj_angle_degrees = math.degrees(obj.angle)
            if (obj_angle_degrees >= min_angle and obj_angle_degrees <= max_angle):
                dir_obj_list.append(obj)

        #Filter obj with same direction
        dir_obj_list=__do_filter_speed__(dir_obj_list,speed_filter)
        for obj in dir_obj_list:
            new_object_list[obj.id]=obj

    return new_object_list