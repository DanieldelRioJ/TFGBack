from  video_generator.filter import ColorFilter,PathFilter,TimeFilter

class FilterQuery:

    def do_filter(self,object_list,color_filter=None,time_filter=None,object_id=None, fps=25):
        if object_id is not None: #If one specific object is requested, return it, otherwise delegate responsibility
            return object_id.get(id)
        object_list=TimeFilter.do_filter(object_list,time_filter,fps)
        object_list=PathFilter.do_filter(object_list)
        return object_list
