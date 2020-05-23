from  virtual_generator.filter import ColorFilter,PathFilter,TimeFilter,AreaFilter,DirectionSpeedFilter,SocialDistanceFilter

def do_filter(object_map, frame_map, filter, pixels_per_meter, fps=25, object_id=None):

    if object_id is not None: #If one specific object is requested, return it, otherwise delegate responsibility
        return object_id.get(id)

    #Try to order them by speed
    object_map=TimeFilter.do_filter(object_map, filter['time'], fps)
    object_map=DirectionSpeedFilter.do_filter(object_map, filter['direction'], filter['speed'])
    object_map=PathFilter.do_filter(object_map, filter['location'])
    object_map=AreaFilter.do_filter(object_map, filter['area'])
    object_map=ColorFilter.do_filter(object_map, filter['outfit'])
    object_map,group_by_social_distance=SocialDistanceFilter.do_filter(object_map, frame_map, pixels_per_meter, filter['social_distance'])
    print("Objects Filtered:" + str(len(object_map)))

    return object_map,group_by_social_distance
