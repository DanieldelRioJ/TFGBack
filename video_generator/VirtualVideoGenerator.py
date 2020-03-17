from io_tools.data import VideoInfDAO
from io_tools.video import VideoRecorder
import cv2
import datetime

#start and end in seconds
def generate_virtual_video(video_obj,movie_script,start=0,duration=10, units="seconds"):

    #Si los valores vienen en segundos, los convertimos a frames
    if units=="seconds":
        start*=video_obj.fps
        duration*=video_obj.fps
    start=int(start)
    duration=int(duration)

    _,_,background_path=VideoInfDAO.get_paths(video_obj)

    background=cv2.imread(background_path)

    lenght=len(movie_script.frame_list)
    end=min(lenght,start+duration)
    imgs=[]
    for i in range (start,end):
        #remember, movie_script frame 1 is in position 0
        frame_script=movie_script.frame_list[i]
        img=background.copy()
        for appearance in frame_script.appearance_list:
            sprite=VideoInfDAO.get_sprit(video_obj,appearance.object.id,appearance.frame)
            aux=img[appearance.row:appearance.row+appearance.h, appearance.col:appearance.col+appearance.w]
            if appearance.overlapped:
                sprite=cv2.addWeighted(sprite, 0.5, aux, 0.5, 0.0)
                #sprite=cv2.scaleAdd(sprite,0.5,aux)
            img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w]=sprite
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=appearance.object.color,
                                thickness=1)
            img = cv2.putText(img, str(appearance.object.id), (appearance.col, appearance.row),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
            img = cv2.putText(img, str(datetime.timedelta(seconds=appearance.frame/7)).split(".")[0], (appearance.col, appearance.row+20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
            img = cv2.putText(img, str(appearance.overlapped), (appearance.col, appearance.row+40),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))
        img=cv2.putText(img, str(i), (0, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        imgs.append(img)

    return VideoRecorder.save_frames_as_video_ffmpeg(video_obj,imgs,movie_script.id,start)