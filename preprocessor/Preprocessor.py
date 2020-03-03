import cv2
from io_tools.annotations.ParserFactory import ParserFactory
from io_tools.video import BackgroundGenerator


class Preprocessor:
    def __init__(self, path_video, path_annotations, chunk_size=10, margin_horizontal=10,margin_vertical=10, block_size=10):
        self.video=cv2.VideoCapture(path_video)
        self.finish=False
        self.chunk_size=chunk_size
        self.object_list,self.frame_dict=ParserFactory.get_parser(path_annotations).parse()
        imgs=self.process_next_chunk()
        self.background=BackgroundGenerator.Background(self.frame_dict,imgs[0],margin_horizontal,margin_vertical ,block_division_size=block_size,sector_size=block_size)

        first_frame=len(imgs)+1
        while not self.has_finished() and not self.background.is_completed():
            imgs=self.process_next_chunk()
            self.background.upgrade(first_frame,imgs[0])
            first_frame +=len(imgs)
            imgs.clear()
            cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", self.background.background)
            cv2.waitKey(10)

        img = self.background.background
        """for appearance in self.frame_dict.get(1):
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)"""
        cv2.imshow("progress", img)
        cv2.waitKey()


    def process_next_chunk(self):
        if not self.video.isOpened():
            raise FileNotFoundError
        frames = []
        i = 1
        while (True):
            ok, frame = self.video.read()
            if not ok:
                self.finish=True
                break
            if i > self.chunk_size:
                break
            frames.append(frame)
            i += 1
        return frames

    def has_finished(self):
        return self.finish

    def close(self):
        self.video.release()