import cv2
from io_tools.annotations.ParserFactory import ParserFactory
from utils.Constants import REPOSITORY_NAME
from preprocessor import BackgroundGenerator,BackgroundGenerator2,BackgroundGenerator3
from io_tools.data import VideoInfDAO,DataSchemeCreator
import threading

class Preprocessor:
    def __init__(self,video_obj,chunk_size=None):

        self.video_name = video_obj.filename
        self.path_video = f"{REPOSITORY_NAME}/videos/{video_obj.name}/"

        self.video=cv2.VideoCapture(f"{self.path_video}{video_obj.filename}")
        if not self.video.isOpened():
            raise FileNotFoundError

        #Modify object with fps, frames, and objects detected
        self.object_dict, self.frame_dict = ParserFactory.get_parser(f"{self.path_video}/{video_obj.annotations_filename}").parse(remove_static_objects=True)
        self.video_obj=video_obj
        self.video_obj.obj_number=len(self.object_dict)
        self.video_obj.fps=self.video.get(cv2.CAP_PROP_FPS)
        self.video_obj.frame_quantity = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        print(f"Name: {self.video_name}, FPS: {self.video_obj.fps}, frames: {self.video_obj.frame_quantity}")

        self.finish=False
        if chunk_size == None: chunk_size=4
        self.chunk_size=chunk_size

        DataSchemeCreator.sprits_dirs_generator(f"{self.path_video}", self.object_dict)
        self.background = BackgroundGenerator3.Backgroundv3(self.frame_dict)

        first_frame=1
        while not self.has_finished():
            imgs=self.process_next_chunk(first_frame)
            self.__process__(first_frame,imgs)
            """i=0
            for img in imgs:
                for appearance in self.frame_dict.get(i+first_frame):
                    img=cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)
                    #img=cv2.putText(img,appearance.object.id,(appearance.col, appearance.row),cv2.FONT_HERSHEY_SIMPLEX,2,2)
                i+=1
                cv2.imshow("video", img)
                cv2.waitKey(50)"""

            #Repeat other iteration trying to improve the background image
            print(first_frame)
            if len(imgs) == 0:
                break
            self.background.upgrade(first_frame,imgs[0])
            first_frame +=len(imgs)

            """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", self.background.background)
            cv2.waitKey(1)"""

            imgs.clear()

        """for appearance in self.frame_dict.get(1):
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)"""
        """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress", img)
        cv2.waitKey()"""

        cv2.imwrite(self.path_video + "background.jpg", self.background.get_background())
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
            """for appearance in self.frame_dict.get(i+first_frame):
                frame = cv2.rectangle(img=frame, pt1=(appearance.col, appearance.row),
                                    pt2=(appearance.col + appearance.w, appearance.row + appearance.h),
                                    color=(0, 0, 255),
                                    thickness=1)
            cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", frame)
            cv2.waitKey(100)"""

            i += 1
        return frames



    def has_finished(self):
        return self.finish

    def close(self):
        self.video.release()