import cv2
from io_tools.annotations.ParserFactory import ParserFactory
from preprocessor import BackgroundGenerator
from io_tools.data import VideoInfDAO,DataSchemeCreator
import threading

class Preprocessor:
    def __init__(self,video_obj, path_video,video_name, path_annotations,chunk_size=None, margin_horizontal=0,margin_vertical=0, block_size=10):
        self.video=cv2.VideoCapture(path_video+video_name)

        self.video_name=video_name
        self.path_video=path_video
        if not self.video.isOpened():
            raise FileNotFoundError

        #Modify object with fps, frames, and objects detected
        self.object_dict, self.frame_dict = ParserFactory.get_parser(path_annotations).parse(remove_static_objects=True)
        self.video_obj=video_obj
        self.video_obj.obj_number=len(self.object_dict)
        self.video_obj.fps=self.video.get(cv2.CAP_PROP_FPS)
        self.video_obj.frame_quantity = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        self.finish=False
        if chunk_size == None: chunk_size=60
        self.chunk_size=chunk_size

        DataSchemeCreator.sprits_dirs_generator(path_video, self.object_dict)
        self.background= BackgroundGenerator.Background(self.frame_dict, margin_horizontal, margin_vertical, block_division_size=block_size, sector_size=block_size)

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

            #Repeat other iteration trying to improve the background image if not finished
            if not self.background.is_completed():
                self.background.upgrade(first_frame,imgs[0])#save image if completed
            first_frame +=len(imgs)

            """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", self.background.background)
            cv2.waitKey(1)"""

            imgs.clear()

        img = self.background.background
        cv2.imwrite(path_video + "background.jpg", self.background.background)
        """for appearance in self.frame_dict.get(1):
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)"""
        """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress", img)
        cv2.waitKey()"""

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