from  virtual_generator.filter import ColorFilter,PathFilter,TimeFilter,AreaFilter,DirectionFilter,SocialDistanceFilter,SpeedFilter

def do_filter(object_map, frame_map, filter, pixels_per_meter, fps=25, object_id=None):

    if object_id is not None: #If one specific object is requested, return it, otherwise delegate responsibility
        return object_id.get(id)

    #Try to order them by speed
    object_map = SpeedFilter.do_filter(object_map, filter.get('speed'))
    object_map=TimeFilter.do_filter(object_map, filter.get('time'), fps)
    object_map=DirectionFilter.do_filter(object_map, filter.get('direction'))
    object_map=PathFilter.do_filter(object_map, filter.get('location'))
    object_map=AreaFilter.do_filter(object_map, filter.get('area'))
    object_map=ColorFilter.do_filter(object_map, filter.get('outfit'))
    object_map,group_by_social_distance=SocialDistanceFilter.do_filter(object_map, frame_map, pixels_per_meter, filter.get('social_distance'))
    print("Objects Filtered:" + str(len(object_map)))

    return object_map,group_by_social_distance
