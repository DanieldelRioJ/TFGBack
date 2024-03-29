import functools

from io_tools.data import VideoInfDAO
from io_tools.video import VideoRecorder
from utils.Constants import *
from multiprocessing.pool import ThreadPool
from matplotlib import pyplot
import numpy as np
import cv2
import os
import datetime

def parallelFunction(script_list, video_obj, background, i):
    # remember, movie_script frame 1 is in position 0
    frame_script = script_list[i]

    img = background.copy()
    for appearance in frame_script.appearance_list:
        sprite = VideoInfDAO.get_sprite(video_obj, appearance.object.id, appearance.frame)
        if appearance.overlapped:
            aux = img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w]
            sprite = cv2.addWeighted(sprite, 0.5, aux, 0.5, 0.0)
            # sprite=cv2.scaleAdd(sprite,0.5,aux)
        img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w] = sprite
        """img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                            pt2=(appearance.col + appearance.w, appearance.row + appearance.h),
                            color=appearance.object.color,
                            thickness=1)"""
        """if(appearance.speed is not None):
            img = cv2.putText(img, "sp:"+str(round(appearance.speed,1)), (appearance.col, appearance.row),
                          cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255))"""
        """img = cv2.putText(img,"col,row:"+
                          str(round(appearance.center_col,2))+","+str(round(appearance.center_row,2)),
                          (appearance.center_col, appearance.center_row + 20),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))"""
        img = cv2.putText(img,
                          str(appearance.object.id),
                          (appearance.center_col, appearance.center_row-20),
                          cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255))
        img = cv2.putText(img, str(datetime.timedelta(seconds=appearance.frame / video_obj.fps_adapted)).split(".")[0],
                          (appearance.center_col-20, appearance.center_row),
                          cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255))
    return img

def parallelFunction2(script_list, video_obj, background, i):
    # remember, movie_script frame 1 is in position 0
    frame_script = script_list[i]

    img = background.copy()
    for appearance in frame_script.appearance_list:
        sprite = VideoInfDAO.get_sprite(video_obj, appearance.object.id, appearance.frame)
        if appearance.overlapped:
            mask=np.zeros((appearance.h,appearance.w,3),dtype=np.uint8)
            for intersection in appearance.overlapped_coordinates:
                x1,y1=int(intersection[0][0]-appearance.col),int(intersection[0][1]-appearance.row)
                x2,y2=int(intersection[1][0]-appearance.col),int(intersection[1][1]-appearance.row)
                mask=cv2.rectangle(mask,(x1,y1),(x2,y2),(128,128,128),-1)


            mask=cv2.GaussianBlur(mask,(5,5),3)
            #cv2.imshow("mask", mask)
            mask=mask/255
            img_background_chunk=img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w]
            left=(img_background_chunk*mask).astype('uint8')
            right=(sprite*(1-mask)).astype('uint8')
            dest=left+right
            """cv2.imshow("left",left)
            cv2.imshow("right",right)
            cv2.imshow("result",dest)
            cv2.waitKey()"""
            img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w]=dest
        else:
            img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w]=sprite

        img = cv2.putText(img,
                          str(appearance.object.id),
                          (appearance.center_col, appearance.center_row-20),
                          cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255))
        img = cv2.putText(img, str(datetime.timedelta(seconds=appearance.frame / video_obj.fps_adapted)).split(".")[0],
                          (appearance.center_col-20, appearance.center_row),
                          cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255))
    return img


#start and end in seconds
def generate_virtual_video(video_obj,movie_script,start=0,duration=10, units="seconds"):
        #Si los valores vienen en segundos, los convertimos a frames
    if units=="seconds":
        start*=video_obj.fps_adapted
        duration*=video_obj.fps_adapted
    start=int(start)
    duration=int(duration)

    video_path = f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}"
    if os.path.isfile(f"{video_path}/virtual/{movie_script.id}/{start}.mp4"):
        return f"{video_path}/virtual/{movie_script.id}/{start}.mp4"

    background_path=VideoInfDAO.get_background_path(video_obj)

    background=cv2.imread(background_path)

    script_list=VideoInfDAO.get_script_list(video_obj,movie_script.id,int(start/(video_obj.fps_adapted*10)))

    lenght=movie_script.frame_quantity-start
    end=min(lenght,duration)
    imgs=[]

    pool=ThreadPool(processes=1)#os.cpu_count()//2)
    imgs=pool.map(functools.partial(parallelFunction2,script_list, video_obj, background), range(0,end))
    return VideoRecorder.save_frames_as_video_ffmpeg(video_obj,VideoInfDAO.get_virtual_video_part_path(video_obj,movie_script.id,start),imgs)