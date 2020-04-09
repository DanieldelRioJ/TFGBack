from helpers import Helper
from objects.Point import Point
import time
import itertools
#It generates a list of frames containing the appearences of the objects suplied in the object_list.
#Each item is a frame.

class MovieScriptFrame(object):
    def __init__(self, frame_number, appearance_list=[]):
        self.frame_number=frame_number
        self.appearance_list=appearance_list

class MovieScript(object):
    def __init__(self,id,frame_list=[]):
        self.id=id
        self.frame_list=frame_list
        self.objects=[]

def group_by_first_frame(object_list):
    frame_group={}
    for id in object_list:
        obj=object_list[id]
        first_frame=obj.appearances[0].frame
        if frame_group.get(first_frame)==None:
            frame_group[first_frame]=[]
        frame_group[first_frame].append(obj)
    return frame_group

def mygrouper(n, iterable):
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.zip_longest(*args))

def generate_movie_script(object_list,video_obj):
    movie_script=__generate_movie_script__(object_list)
    movie_script.frame_quantity=len(movie_script.frame_list)
    movie_script.objects_quantity=len(object_list)
    frame_lists=list(mygrouper(int(video_obj.fps_adapted)*10,movie_script.frame_list))
    movie_script.frame_list=None
    movie_script.objects=object_list.copy()
    for obj_id in object_list:
        movie_script.objects[obj_id].appearances=None
    return movie_script,frame_lists

#Divided in general script and chunk scripts
def __generate_movie_script__(object_list):
    frame_group=group_by_first_frame(object_list)
    frame_list=[]
    first_possible_frame=1
    for frame_number in frame_group:
        group=frame_group[frame_number]
        #give us the first frame where we can include the object
        frame_number= __first_frame_available__(frame_list,group, 1)
        print(frame_number,first_possible_frame)
        first_possible_frame=frame_number
        for obj in group:
            first_frame_aux=frame_number
            #Anhadimos las apariciones a los respectivos frames
            for appearance in obj.appearances:
                if first_frame_aux > len(frame_list): #Extend list
                    frame_list.append(MovieScriptFrame(first_frame_aux,[]))

                for appearance2 in frame_list[first_frame_aux-1].appearance_list: #Check if overlap, for make it transparent
                    if Helper.do_overlap(Point(appearance2.col,appearance2.row),
                                     Point(appearance2.col+appearance2.w, appearance2.row+appearance2.h),
                                     Point(appearance.col,appearance.row),
                                     Point(appearance.col+appearance.w,appearance.row+appearance.h)):
                        appearance.overlapped=True
                        #appearance2.overlapped=True
                        break

                frame_list[first_frame_aux-1].appearance_list.append(appearance)
                first_frame_aux+=1
    return MovieScript(format(int(time.time() * 1000000),'x'),frame_list)




#It tell us in wich frame can the object be included (remember that gt.txt frame number starts on 1, here we start also on 1)
def __first_frame_available__(frame_list, frame_group, first_posible_frame=1):
    i=first_posible_frame
    for frame in frame_list[i-1:]:
        overlapped=False
        for obj in frame_group:
            obj_a=obj.appearances[0]
            for appearance in frame.appearance_list:
                if Helper.do_overlap(Point(obj_a.col,obj_a.row),
                                     Point(obj_a.col+obj_a.w, obj_a.row+obj_a.h),
                                     Point(appearance.col,appearance.row),
                                     Point(appearance.col+appearance.w,appearance.row+appearance.h)):
                    overlapped=True
                    break
            if overlapped: #Hay un objeto ocupando el lugar
                break
        if not overlapped:  #El frame ya existe y está libre la zona
            return i
        i += 1
    return i
