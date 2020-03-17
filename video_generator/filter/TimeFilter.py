
class TimeFilter:
    #'seconds' and 'frames' available
    def __init__(self, start, end, units="frames"):
        self.start=start
        self.end=end
        self.units=units

def do_filter(object_list,time_filter:TimeFilter=None,fps=25):
    if time_filter is None:
        return object_list

    if time_filter.units=='seconds':
        time_filter.start*=fps
        time_filter.end*=fps

    aux_list={}
    for id in object_list:
        obj=object_list[id]
        if obj.appearances[-1].frame >= time_filter.start and obj.appearances[0].frame <= time_filter.end:
            aux_list[id]=obj

    return aux_list
