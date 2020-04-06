def do_filter(object_list,speed_filter, fps):
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