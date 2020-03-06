import cv2
from io_tools.annotations.ParserFactory import ParserFactory
from preprocessor import BackgroundGenerator
from io_tools.data import VideoInfDAO,DataSchemeCreator


class Preprocessor:
    def __init__(self, path_video,video_name, path_annotations,chunk_size=None, margin_horizontal=0,margin_vertical=0, block_size=10):
        self.video=cv2.VideoCapture(path_video+video_name)
        if not self.video.isOpened():
            raise FileNotFoundError
        self.finish=False
        if chunk_size == None: chunk_size=60
        self.chunk_size=chunk_size
        self.object_list,self.frame_dict=ParserFactory.get_parser(path_annotations).parse()
        #DataSchemeCreator.sprits_dirs_generator(video_name)
        self.background= BackgroundGenerator.Background(self.frame_dict, margin_horizontal, margin_vertical, block_division_size=block_size, sector_size=block_size)

        first_frame=1
        while not self.has_finished() and not self.background.is_completed():
            imgs=self.process_next_chunk(first_frame)
            #VideoInfDAO.save_sprits(first_frame,self.frame_dict,imgs)
            #self.__process__(first_frame,imgs)
            """i=0
            for img in imgs:
                for appearance in self.frame_dict.get(i+first_frame):
                    img=cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)
                i+=1
                cv2.imshow("video", img)
                cv2.waitKey(50)"""

            if not self.background.is_completed():
                if self.background.upgrade(first_frame,imgs[0]):
                    cv2.imwrite(path_video+"background.jpg",self.background.background)
            first_frame +=len(imgs)

            """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", self.background.background)
            cv2.waitKey(1)"""

            imgs.clear()

        img = self.background.background
        """for appearance in self.frame_dict.get(1):
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)"""
        cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress", img)
        cv2.waitKey()

    def __process__(self,first_frame,imgs):
        i=0
        for img in imgs:
            frame_number=first_frame+i
            for appearance in self.frame_dict.get(frame_number):
                pass
            i+=1

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