import cv2
from preprocessor import BackgroundGenerator3
from io_tools.data import VideoInfDAO,DataSchemeCreator
from io_tools.annotations import MOTParser
from helpers import Helper,LinearRegressionHelper,OutfitHelper
import threading
from objects import Point


class Preprocessor:
    def __init__(self,video_obj,chunk_size=None):
        self.video=cv2.VideoCapture(VideoInfDAO.get_original_video_path(video_obj))
        if not self.video.isOpened():
            raise FileNotFoundError

        #Modify object with fps, frames, and objects detected
        self.object_dict, self.frame_dict = VideoInfDAO.get_video_objects(video_obj,adapted=False,remove_static_objects=True)
        self.video_obj=video_obj
        self.video_obj.obj_number=len(self.object_dict)
        self.video_obj.fps=self.video.get(cv2.CAP_PROP_FPS)
        self.deleted_frames=[]

        #space between eliminations (1 = 1 frame between each elimination, 2=2 frame between elimination... etc)
        if self.video_obj.fps>10:
            rest=self.video_obj.fps-10
            self.frame_space=self.video_obj.fps / rest;
            self.video_obj.fps_adapted=10
        else: #if fps is less than 10, dont do anything
            self.video_obj.fps_adapted=self.video_obj.fps
            self.frame_space=-1

        self.eliminated_frame_number=0
        self.sum_of_spaces=0

        self.new_frame_map={}

        self.video_obj.frame_quantity = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        print(f"Name: movie.mp4, FPS: {self.video_obj.fps}, frames: {self.video_obj.frame_quantity}")

        self.finish=False
        if chunk_size == None: chunk_size=4
        self.chunk_size=chunk_size

        print("CHUNK SIZE:"+str(chunk_size))

        DataSchemeCreator.sprites_dirs_generator(VideoInfDAO.get_video_base_dir(video_obj), self.object_dict)
        self.background = BackgroundGenerator3.Backgroundv3(self.frame_dict)

        first_real_frame=1
        while not self.has_finished():
            imgs=self.process_next_chunk(first_real_frame)
            self.__process__(first_real_frame, imgs)

            #Repeat other iteration trying to improve the background image
            #print(first_real_frame)
            if len(imgs) == 0:
                break
            self.background.upgrade(first_real_frame, imgs[0])
            first_real_frame +=len(imgs)
            imgs.clear()

        background_image=self.background.get_background()
        VideoInfDAO.save_background(self.video_obj,background_image,30)
        self.video_obj.width = background_image.shape[1]
        self.video_obj.height = background_image.shape[0]

        #Get more information (path, direction, speed etc).
        self.object_dict=Helper.convert_frame_map_to_object_map(self.new_frame_map,self.object_dict)
        #Calculate speed
        for obj_id in self.object_dict:
            obj=self.object_dict.get(obj_id)
            appearances=obj.appearances
            last_appearance=appearances[0]
            biggerArea=0
            if(last_appearance.center_col==None):
                last_appearance.center_col, last_appearance.center_row=__calculate_center__(last_appearance)

            speed=0 #For calculation of average speed
            for appearance in appearances[1:]:

                #Calculate bigger picture for portrait
                area=appearance.w*appearance.h
                if area>biggerArea:
                    obj.portrait=appearance.frame
                    biggerArea=area


                #Calculate speed
                appearance.center_col, appearance.center_row = __calculate_center__(appearance)
                appearance.speed=Helper.distance(appearance.center_col,appearance.center_row,last_appearance.center_col,last_appearance.center_row)
                speed+=appearance.speed #used in calculation of average speed
                last_appearance=appearance
            __set_object_angle_direction_and_speed__(obj)
            path_image=background_image.copy()
            path_image=__draw_path__(path_image,[(int(appearance.center_col),int(appearance.center_row)) for appearance in obj.appearances[::10]])
            VideoInfDAO.save_sprite(video_obj, "path", obj.id, path_image)

        #Arrange gt, maybe some points are outside the box
        for obj_id in self.object_dict:
            obj=self.object_dict.get(obj_id)
            for appearance in obj.appearances:
                row1,row2,col1,col2=Helper.get_points(self.video_obj.height,self.video_obj.width,appearance.row,appearance.row+appearance.h,appearance.col,appearance.col+appearance.w)
                appearance.row=row1
                appearance.col=col1
                appearance.w=col2-col1
                appearance.h=row2-row1

        OutfitHelper.obtain_object_colors(self.video_obj, self.object_dict)
        VideoInfDAO.save_gt_adapted(self.video_obj, MOTParser.parse_back(self.new_frame_map, self.object_dict))



        print("Finished!")
        self.video_obj.frame_quantity_adapted=self.video_obj.frame_quantity-self.eliminated_frame_number
        self.video_obj.processed=True

    def __process__(self, first_real_frame, imgs):
        i=-1
        for img in imgs:
            self.sum_of_spaces+=1
            i += 1
            frame_number= first_real_frame + i
            if self.sum_of_spaces<self.frame_space or self.frame_space==-1: #Si no se elimina
                if self.frame_dict.get(frame_number) is None: continue  # Si no aparecen objetos, seguimos
                for appearance in self.frame_dict.get(frame_number):
                    cutout = img[appearance.row:appearance.row + appearance.h,
                             appearance.col:appearance.col + appearance.w]
                    threading.Thread(target=VideoInfDAO.save_sprite, args=(
                    self.video_obj, frame_number - self.eliminated_frame_number, appearance.object.id,
                    cutout)).start()
                    # Update frame number (remember the eliminations)
                    appearance.frame = appearance.frame - self.eliminated_frame_number
                self.new_frame_map[frame_number - self.eliminated_frame_number] = self.frame_dict.get(frame_number)

            else: #eliminamos frame
                self.eliminated_frame_number+=1
                self.sum_of_spaces-=self.frame_space
                self.deleted_frames.append(frame_number)
                continue


    def process_next_chunk(self,first_frame):
        frames = []
        i = 0
        while (True):
            ok, frame = self.video.read()
            if not ok:
                self.finish=True
                break
            if i >= self.chunk_size:
                frames.append(frame)
                break
            frames.append(frame)
            i += 1
        return frames

    def has_finished(self):
        return self.finish

    def close(self):
        self.video.release()

def __calculate_center__(appearance):
    return (appearance.col * 2 + appearance.w) / 2, (appearance.row * 2 + appearance.h) / 2

def __set_object_angle_direction_and_speed__(obj):
    if obj.id==98:
        print('')
    angle,distance=LinearRegressionHelper.get_direction_angle([Point.Point(appearance.center_col,appearance.center_row) for appearance in obj.appearances])

    obj.angle=angle
    if distance is not None:
        obj.average_speed=distance/len(obj.appearances)

def __draw_path__(path_image, points):
    last_point=points[0]
    for point in points[1:-1]:
        path_image=cv2.line(path_image, last_point, point, (0, 0, 255), 5, cv2.FILLED)
        last_point=point
    second_last_point=points[-min(len(points),2)]
    distance_last_points=Helper.distance(*second_last_point,*points[-1])
    if distance_last_points==0:
        distance_last_points=20
    path_image=cv2.arrowedLine(path_image, second_last_point,points[-1], (0, 0, 255), 5, cv2.FILLED,tipLength=20/distance_last_points)
    return path_image

