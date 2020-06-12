from helpers import Helper

def __is_group_in_list__(group,list):
    for g in list:
        if group is g:
            return True
    return False


def do_filter(object_map,frame_map, units_per_meter, social_distance):
    if social_distance is None or social_distance.get('distance') is None or units_per_meter is None:
        return object_map,None

    distance=int(social_distance['distance'])*(1.7*units_per_meter) #+width of a person
    new_obj_map={}


    for frame_number,appearances in frame_map.items():

        for i in range(0,len(appearances)-1):
            apA=appearances[i]
            if frame_number == 43:
                print("hallo")
            for j in range(i+1,len(appearances)):
                apB=appearances[j]

                auxxx=Helper.distance(*apA.real_coordinates,*apB.real_coordinates)
                #if collision, add to group
                if Helper.distance(*apA.real_coordinates,*apB.real_coordinates)<distance:
                    new_obj_map[apA.object.id]=apA.object
                    new_obj_map[apB.object.id] = apB.object

                    if apA.object.group==None and apB.object.group==None:
                        group={}
                        group[apA.object.id] = apA.object
                        group[apB.object.id] = apB.object
                        apA.object.group=group
                        apB.object.group=group
                    elif apA.object.group!=None and apB.object.group==None:
                        group=apA.object.group
                        apB.object.group=group
                        group[apB.object.id] = apB.object
                    elif apA.object.group==None and apB.object.group!=None:
                        group=apB.object.group
                        apA.object.group = group
                        group[apA.object.id] = apA.object
                    else:#Both has group
                        #we have to mix groups if they are different, if they are the same, we dont need to do anything
                        if apA.object.group is not apB.object.group:
                            groupA=apA.object.group
                            groupB=apB.object.group
                            for id, obj in groupB.items():
                                groupA[id]=obj
                                obj.group=groupA
                            groupB.clear()

    #Collect groups
    group_list=[]
    for _, obj in new_obj_map.items():
        if obj.group is not None and not __is_group_in_list__(obj.group,group_list):
            group_list.append(obj.group)

    for group in group_list:
        first_obj=next(iter(group.values()))
        first_app=first_obj.first_appearance
        last_app=first_obj.last_appearance
        for id,obj in group.items():
            try:
                a=obj.first_appearance
            except AttributeError:
                print("error")
            if obj.first_appearance< first_app:
                first_app=obj.first_appearance
            if obj.last_appearance>last_app:
                last_app=obj.last_appearance
        group['first_appearance']=first_app
        group['last_appearance'] = last_app

    return new_obj_map,group_list