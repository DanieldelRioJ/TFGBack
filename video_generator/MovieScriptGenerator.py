from helpers import Helper
from objects.Point import Point
import time
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


def generate_movie_script(object_list):
    frame_list=[]
    for id in object_list:
        obj=object_list[id]
        #give us the first frame where we can include the object
        frame_number= __first_frame_available__(frame_list,obj)

        #Anhadimos las apariciones a los respectivos frames
        for appearance in obj.appearances:
            if frame_number > len(frame_list): #Extend list
                frame_list.append(MovieScriptFrame(frame_number,[]))

            for appearance2 in frame_list[frame_number-1].appearance_list:
                if Helper.do_overlap(Point(appearance2.col,appearance2.row),
                                 Point(appearance2.col+appearance2.w, appearance2.row+appearance2.h),
                                 Point(appearance.col,appearance.row),
                                 Point(appearance.col+appearance.w,appearance.row+appearance.h)):
                    appearance.overlapped=True
                    #appearance2.overlapped=True
                    break

            frame_list[frame_number-1].appearance_list.append(appearance)
            frame_number+=1
    return MovieScript(format(int(time.time() * 1000000),'x'),frame_list)




#It tell us in wich frame can the object be included (remember that gt.txt frame number starts on 1, here we start also on 1)
def __first_frame_available__(frame_list, obj):
    i=1
    obj_a=obj.appearances[0]
    for frame in frame_list:
        overlapped=False
        for appearance in frame.appearance_list:
            if Helper.do_overlap(Point(obj_a.col,obj_a.row),
                                 Point(obj_a.col+obj_a.w, obj_a.row+obj_a.h),
                                 Point(appearance.col,appearance.row),
                                 Point(appearance.col+appearance.w,appearance.row+appearance.h)):
                overlapped=True
                break
        if not overlapped: #El frame ya existe y está libre la zona
            return i
        i += 1
    return i