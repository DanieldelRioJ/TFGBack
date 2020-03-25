import time
import datetime


class TimeFilter:
    #'seconds' and 'frames' available
    def __init__(self, start, end):
        self.start=start
        self.end=end

def timeToFrame(t,fps):
    t=time.strptime(t,'%H:%M:%S')
    t=datetime.timedelta(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec).total_seconds()
    return t*fps

def do_filter(object_list,time_filter:TimeFilter=None,fps=25):
    if time_filter is None or not time_filter:
        return object_list

    if time_filter['start']!="":
        time_filter['start']=timeToFrame(time_filter['start'], fps)
        if time_filter['end'] != "":
            time_filter['end'] = timeToFrame(time_filter['end'], fps)

    aux_list={}
    for id in object_list:
        obj=object_list[id]
        if ( time_filter['start']=="" or obj.appearances[-1].frame >= time_filter['start'] ) and ( time_filter["end"]=="" or obj.appearances[0].frame <= time_filter['end'] ):
            aux_list[id]=obj

    return aux_list
