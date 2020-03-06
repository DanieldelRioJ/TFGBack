import json
import os
import threading
from utils.Constants import REPOSITORY_NAME,VIDEOS_FILE,VIDEOS_DIR,SPRITES_DIR
from exceptions.VideoRepeated import VideoRepeated
from preprocessor import Preprocessor
import subprocess

from werkzeug.utils import secure_filename

lock=threading.Lock()

def get_video_index():
    with open(REPOSITORY_NAME) as file:
        json_data=json.load(file)
    return json_data

def add_video(video_obj, video, annotations):
    with lock:
        with open(REPOSITORY_NAME+os.path.sep+VIDEOS_FILE,"r+") as file:
            json_data=json.load(file)
            for v in json_data:
                if v['name']==video_obj['name']:
                    raise VideoRepeated
            __write_video__(video_obj,video,annotations)
            json_data.append(video_obj)
            file.seek(0)
            json.dump(json_data,file)
    return video_obj

def set_video_as_processed(video_name):
    obj=None
    with lock:
        with open(REPOSITORY_NAME + os.path.sep + VIDEOS_FILE, "r+") as file:
            json_data = json.load(file)
            for v in json_data:
                if v['name'] == video_name:
                    v['processed']=True
                    file.seek(0)
                    json.dump(json_data, file)
                    obj=v
                    break;
    return obj

def __write_video__(video_obj,video,annotations):

    video.filename=secure_filename(video.filename)
    annotations.filename = secure_filename(annotations.filename)
    video_dir=REPOSITORY_NAME+os.path.sep+VIDEOS_DIR+os.path.sep+video_obj['name']+os.path.sep
    #.repository/videos/{video_obj.name}
    os.makedirs(video_dir+SPRITES_DIR)
    video.save(video_dir+video_obj['name'])
    annotations.save(video_dir+annotations.filename)

    command = f"ffmpeg -i {video_dir}{video_obj['name']} -preset superfast {video_dir}.{video_obj['name']}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    Preprocessor.Preprocessor(video_dir,f".{video_obj['name']}", f"{video_dir}{annotations.filename}",margin_horizontal=10,margin_vertical=10).close()

def save_sprits(first_frame,video_name,frame_dict,imgs):
    video_dir = REPOSITORY_NAME + os.path.sep + VIDEOS_DIR + os.path.sep + video_name + os.path.sep+SPRITES_DIR+os.path.sep
    print("oal")
    pass