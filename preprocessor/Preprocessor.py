import cv2
from io_tools.annotations.ParserFactory import ParserFactory
from utils.Constants import REPOSITORY_NAME
from preprocessor import BackgroundGenerator3
from io_tools.data import VideoInfDAO,DataSchemeCreator
from io_tools.annotations import MOTParser
from helpers import Helper
import threading
import math

class Preprocessor:
    def __init__(self,video_obj,chunk_size=None):

        self.path_video = f"{REPOSITORY_NAME}/videos/{video_obj.id}/"

        self.video=cv2.VideoCapture(f"{self.path_video}video.mp4")
        if not self.video.isOpened():
            raise FileNotFoundError

        #Modify object with fps, frames, and objects detected
        self.object_dict, self.frame_dict = ParserFactory.get_parser(f"{self.path_video}/gt.txt").parse(remove_static_objects=True)
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

        DataSchemeCreator.sprits_dirs_generator(f"{self.path_video}", self.object_dict)
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

        VideoInfDAO.save_background(self.video_obj,self.background.get_background(),30)

        #Get more information (path, direction, speed etc).
        self.object_dict=Helper.convert_frame_map_to_object_map(self.new_frame_map,self.object_dict)
        for obj_id in self.object_dict:
            appearances=self.object_dict.get(obj_id).appearances
            last_appearance=appearances[0]
            if(last_appearance.center_col==None):
                last_appearance.center_col, last_appearance.center_row=__calculate_center__(last_appearance)
            for appearance in appearances[1:]:
                appearance.center_col, appearance.center_row = __calculate_center__(appearance)
                col,row=appearance.center_col-last_appearance.center_col,appearance.center_row-last_appearance.center_row
                appearance.speed=math.sqrt((row**2)+(col**2))
                last_appearance=appearance
        VideoInfDAO.save_gt_adapted(self.video_obj,MOTParser.parseBack(self.new_frame_map))


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
                    threading.Thread(target=VideoInfDAO.save_sprit, args=(
                    self.path_video, frame_number - self.eliminated_frame_number, appearance.object.id,
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