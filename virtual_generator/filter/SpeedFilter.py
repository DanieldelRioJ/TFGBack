import numpy as np

"""def do_filter(object_list,speed_filter, fps):
    min=speed_filter['min']
    max=speed_filter['max']
    time=0;
    if speed_filter['time'] is not None:
        time=speed_filter['time']
        time*=fps #convert time in seconds to time in frames
    new_list={}
    for id in object_list:
        obj=object_list[id]
        counter=0
        for appearance in obj.appearances[1:]: #First appearance has speed none because cant not be calculated with previous positions
            if (min==None or min<=appearance.speed) and (max==None or max>=appearance.speed): #If speed inside values
                counter+=1
                if counter > time: #If counter inside time parameter
                    new_list[id]=obj
                    break
    return new_list
"""


#Filter obj
def do_filter(obj_dict, speed_filter):
    if speed_filter is None:
        return obj_dict
    speed_filter_bool=[speed_filter.get("very_slow"), speed_filter.get("slow"), speed_filter.get("normal"),
                       speed_filter.get("fast"), speed_filter.get("very_fast")]
    if speed_filter_bool is None or all(speed == 0 for speed in speed_filter_bool):
        return obj_dict

    speed_lists=[obj.average_speed for id,obj in obj_dict.items() if obj.average_speed!=None]
    mean = np.mean(speed_lists)
    std=np.std(speed_lists)


    aux_dict={}
    #Very slow is <=-1.5std, slow is >-1.5std and <-0.5std
    #Normal is >=-0.5std and <=0.5std
    #Fast is >0.5std and <1.5std, very fast is >=1.5std
    for id,obj in obj_dict.items():
        if obj.average_speed is None:
            continue
        desviation=obj.average_speed-mean
        if desviation<=-1.5*std and speed_filter_bool[0]:
            aux_dict[id]=obj
        elif desviation>-1.5*std and desviation<-0.5*std and speed_filter_bool[1]:
            aux_dict[id]=obj
        elif desviation>=-0.5*std and desviation<=0.5*std and speed_filter_bool[2]:
            aux_dict[id]=obj
        elif desviation>0.5*std and desviation<1.5*std and speed_filter_bool[3]:
            aux_dict[id]=obj
        elif desviation>=1.5*std and speed_filter_bool[4]:
            aux_dict[id]=obj
    return aux_dict