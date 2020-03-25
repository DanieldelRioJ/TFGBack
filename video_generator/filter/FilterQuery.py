from  video_generator.filter import ColorFilter,PathFilter,TimeFilter

def do_filter(object_list,filter, fps=25,object_id=None):

    if object_id is not None: #If one specific object is requested, return it, otherwise delegate responsibility
        return object_id.get(id)


    object_list=TimeFilter.do_filter(object_list,filter['time'],fps)
    object_list=PathFilter.do_filter(object_list)
    return object_list
