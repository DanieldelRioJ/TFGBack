import cv2
from io_tools.annotations.ParserFactory import ParserFactory
from utils.Constants import REPOSITORY_NAME
from preprocessor import BackgroundGenerator,BackgroundGenerator2,BackgroundGenerator3
from io_tools.data import VideoInfDAO,DataSchemeCreator
import threading

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
        self.video_obj.frame_quantity = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        print(f"Name: movie.mp4, FPS: {self.video_obj.fps}, frames: {self.video_obj.frame_quantity}")

        self.finish=False
        if chunk_size == None: chunk_size=4
        self.chunk_size=chunk_size

        DataSchemeCreator.sprits_dirs_generator(f"{self.path_video}", self.object_dict)
        self.background = BackgroundGenerator3.Backgroundv3(self.frame_dict)

        first_frame=1
        while not self.has_finished():
            imgs=self.process_next_chunk(first_frame)
            self.__process__(first_frame,imgs)

            #Repeat other iteration trying to improve the background image
            print(first_frame)
            if len(imgs) == 0:
                break
            self.background.upgrade(first_frame,imgs[0])
            first_frame +=len(imgs)
            imgs.clear()

        cv2.imwrite(self.path_video + "background.jpg", self.background.get_background(),[cv2.IMWRITE_JPEG_QUALITY, 9])
        print("Finished!")
        self.video_obj.processed=True

    def __process__(self,first_frame,imgs):
        i=-1
        for img in imgs:
            i += 1
            frame_number=first_frame+i
            if self.frame_dict.get(frame_number) == None: continue
            for appearance in self.frame_dict.get(frame_number):
                if(frame_number==1 and appearance.object.id==10):
                    pass
                cutout=img[appearance.row:appearance.row+appearance.h,appearance.col:appearance.col+appearance.w]
                threading.Thread(target=VideoInfDAO.save_sprit,args=(self.path_video,frame_number,appearance.object.id,cutout)).start()
                #VideoInfDAO.save_sprit(self.path_video,frame_number,appearance.object.id,cutout)

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