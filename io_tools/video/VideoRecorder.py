import cv2
import subprocess
import os
import datetime

def save_frames_as_video_opencv(file_path,imgs, fps):
    height, width, layers = imgs[0].shape
    #out= cv2.VideoWriter(filename=file_path,fourcc=cv2.VideoWriter_fourcc(*'avc1'), fps=fps,frameSize= (width,height),isColor=True)
    out = cv2.VideoWriter(filename=file_path, fourcc=cv2.VideoWriter_fourcc(*'VP80'), fps=fps,
                          frameSize=(width, height), isColor=True)
    for img in imgs:
        out.write(img)
    out.release()

def save_frames_as_video_ffmpeg(file_path,imgs,fps):
    temporal_dir_name="temporal"
    os.mkdir(temporal_dir_name)
    index=1
    for img in imgs:
        name=temporal_dir_name+"/{index:06}.jpg".format(index=index)
        print(name)
        cv2.imwrite(name,img)
        index+=1

    #command=f"ffmpeg -r {fps} -i {temporal_dir_name}/%06d.jpg -vcodec libvpx -acodec libvorbis -deadline good -crf 4 {file_path}"
    command=f"ffmpeg -r 7 -i {temporal_dir_name}/%06d.jpg -c:v libx264 -profile:v main -level 3.2 -pix_fmt yuv420p -preset fast -tune zerolatency -flags +cgop+low_delay -movflags empty_moov+omit_tfhd_offset+frag_keyframe+default_base_moof+isml -c:a aac {file_path}.mp4"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()