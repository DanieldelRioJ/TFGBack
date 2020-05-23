from helpers import Helper
from objects.Point import Point
from shapely.geometry import Polygon
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

def mygrouper(n, iterable):
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.zip_longest(*args))

def generate_movie_script(object_list,group,video_obj):
    movie_script=__generate_movie_script__(object_list,group)
    movie_script.frame_quantity=len(movie_script.frame_list)
    movie_script.objects_quantity=len(object_list)
    frame_lists=list(mygrouper(int(video_obj.fps_adapted)*10,movie_script.frame_list))
    movie_script.frame_list=None
    movie_script.objects=object_list.copy()
    for obj_id in object_list:
        movie_script.objects[obj_id].appearances=None
    return movie_script,frame_lists

#Divided in general script and chunk scripts
def __generate_movie_script__(object_list,groups):
    frame_list=[]
    first_possible_frame=1
    for group in groups:
        #give us the first frame where we can include the object
        frame_number= __first_frame_available__(frame_list,group, 1)
        print(frame_number,first_possible_frame)
        first_possible_frame=frame_number

        n_frames=group['last_appearance']-group['first_appearance']-(len(frame_list)-first_possible_frame)
        for i in range(n_frames+1):
            frame_list.append(MovieScriptFrame(first_possible_frame+i, []))

        for id,obj in group.items():
            if(isinstance(id, str)):
                continue
            first_frame_aux=frame_number+obj.first_appearance-group['first_appearance']
            #Anhadimos las apariciones a los respectivos frames
            for appearance in obj.appearances:
                """if first_frame_aux > len(frame_list): #Extend list
                    frame_list.append(MovieScriptFrame(first_frame_aux,[]))"""

                #Will store coordinates of polygons wich represent the intersectio between this appearance
                #and another appearances
                appearance.overlapped_coordinates=[]
                for appearance2 in frame_list[first_frame_aux-1].appearance_list: #Check if overlap, for make it transparent
                    if obj.first_appearance!=appearance2.object.first_appearance and Helper.do_overlap(Point(appearance2.col,appearance2.row),
                                     Point(appearance2.col+appearance2.w, appearance2.row+appearance2.h),
                                     Point(appearance.col,appearance.row),
                                     Point(appearance.col+appearance.w,appearance.row+appearance.h)):
                        appearance.overlapped=True
                        polygon_a=Helper.get_polygon_by_appearance(appearance)
                        polygon_b=Helper.get_polygon_by_appearance(appearance2)

                        polygon_intersection=polygon_a.intersection(polygon_b)

                        #If the intersection is a line
                        if polygon_intersection.area==0:
                            continue
                        coordinates=[(polygon_intersection.bounds[0],polygon_intersection.bounds[1]),(polygon_intersection.bounds[2],polygon_intersection.bounds[3])]
                        appearance.overlapped_coordinates.append(coordinates)

                frame_list[first_frame_aux-1].appearance_list.append(appearance)
                first_frame_aux+=1
    return MovieScript(format(int(time.time() * 1000000),'x'),frame_list)




#It tell us in wich frame can the object be included (remember that gt.txt frame number starts on 1, here we start also on 1)
def __first_frame_available__(frame_list, frame_group, first_posible_frame=1):
    return 1
