import functools

import cv2
import subprocess
import pathlib
import os
import shutil
from utils.Constants import *
import time
from multiprocessing.pool import ThreadPool

def save_frames_as_video_opencv(file_path,imgs, fps):
    height, width, layers = imgs[0].shape
    #out= cv2.VideoWriter(filename=file_path,fourcc=cv2.VideoWriter_fourcc(*'avc1'), fps=fps,frameSize= (width,height),isColor=True)
    out = cv2.VideoWriter(filename=file_path, fourcc=cv2.VideoWriter_fourcc(*'VP80'), fps=fps,
                          frameSize=(width, height), isColor=True)
    for img in imgs:
        out.write(img)
    out.release()

def __save_frame__(temporal_dir_name, img,index):
    name = temporal_dir_name + "/{index:06}.jpg".format(index=index)
    cv2.imwrite(name, img)

def save_frames_as_video_ffmpeg(video_obj,file_path,imgs):
    temporal_id=format(int(time.time() * 1000000),'x')
    video_path=pathlib.Path(file_path).parent
    temporal_dir_name=f"{video_path}/temporal/{temporal_id}"
    os.makedirs(temporal_dir_name)
    pool=ThreadPool(processes=os.cpu_count()//2)

    print("Start recording frames")
    pool.starmap(functools.partial(__save_frame__,temporal_dir_name),zip(imgs,range(1,len(imgs)+1)))
    print("Stop recording frames")

    command = f"ffmpeg -y -r {video_obj.fps_adapted} -i {temporal_dir_name}/%06d.jpg -profile:v main -g -1 \
            -preset ultrafast -c:v libx264 \
            -f mp4 -flags +cgop+low_delay -movflags empty_moov+omit_tfhd_offset+frag_keyframe+default_base_moof+isml \
            {file_path}"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    shutil.rmtree(temporal_dir_name, ignore_errors=True)

    return file_path

def generate_individual_video(video_obj,video_obj_opencv,obj):
    temporal_id = format(int(time.time() * 1000000), 'x')
    video_path = f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}"
    temporal_dir_name = f"{video_path}/temporal/{temporal_id}"
    os.makedirs(temporal_dir_name)

    video_obj_opencv.set(1, obj.first_appearance - 1) #CAP_PROP_POS_FRAMES = 1
    for i,appearance in enumerate(obj.appearances):
        res,img=video_obj_opencv.read()
        img=cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                            pt2=(appearance.col + appearance.w, appearance.row + appearance.h),
                            color=(0,0,255),
                            thickness=3)
        __save_frame__(temporal_dir_name,img,i)

    command = f"ffmpeg -y -r {video_obj.fps_adapted} -i {temporal_dir_name}/%06d.jpg -preset ultrafast {video_path}/sprites/{obj.id}/alone.mp4"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    shutil.rmtree(temporal_dir_name, ignore_errors=True)






#command=f"ffmpeg -r {fps} -i {temporal_dir_name}/%06d.jpg -vcodec libvpx -acodec libvorbis -deadline good -crf 4 {file_path}"
"""command=f"ffmpeg -y -r {video_obj.fps} -i {temporal_dir_name}/%06d.jpg -c:v libx264 -profile:v main -level 3.2 " \
        f"-pix_fmt yuv420p -preset ultrafast -tune zerolatency -flags +cgop+low_delay -movflags empty_moov+omit_tfhd_offset+frag_keyframe+default_base_moof+isml " \
        f"-c:a aac {video_path}/virtual/{movie_script_id}/{start}.mp4"""

"""command = f"ffmpeg -y -r {video_obj.fps} -i {temporal_dir_name}/%06d.jpg -c:v libx264 -profile:v main -level 3.2 " \
          f"-preset ultrafast -tune zerolatency -flags +cgop+low_delay -movflags empty_moov+omit_tfhd_offset+frag_keyframe+default_base_moof+isml " \
          f"{video_path}/virtual/{movie_script_id}/{start}.mp4" """