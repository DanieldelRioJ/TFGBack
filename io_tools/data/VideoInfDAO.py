import json
import os
import threading
from utils.Constants import REPOSITORY_NAME,VIDEOS_FILE,VIDEOS_DIR,SPRITES_DIR
from exceptions.VideoRepeated import VideoRepeated
from preprocessor import Preprocessor
import subprocess
import cv2

from werkzeug.utils import secure_filename

lock=threading.Lock()
index_file=REPOSITORY_NAME+os.path.sep+VIDEOS_FILE

def get_video_index():
    with open(index_file) as file:
        json_data=json.load(file)
    return json_data

def get_video(name):
    with open(index_file) as file:
        json_data=json.load(file)
        for v in json_data:
            if v['name']==name:
                return v
    return None

def deleteAll():
    with open(index_file,'r+') as file:
        file.truncate(0)
        file.write('[]')
    return True

def delete(video_name):
    with open(index_file,'r+') as file:
        json_data = json.load(file)
        for v in json_data:
            if v['name'] == video_name:
                json_data.remove(v)
                file.seek(0)
                file.truncate(0)
                json.dump(json_data,file)
                return True
    return False

def add_video(video_obj, video, annotations):
    with lock:
        with open(index_file,"r+") as file:
            json_data=json.load(file)
            for v in json_data:
                if v['name']==video_obj.name:
                    raise VideoRepeated

            #Save Video
            video.filename = secure_filename(video.filename)
            annotations.filename = secure_filename(annotations.filename)
            video_dir = REPOSITORY_NAME + os.path.sep + VIDEOS_DIR + os.path.sep + video_obj.name + os.path.sep

            # .repository/videos/{video_obj.name}
            os.makedirs(video_dir)
            video.save(video_dir + video.filename)
            annotations.save(video_dir + annotations.filename)

            x = threading.Thread(target=__write_video__, args=(video_obj,video_dir,video.filename,annotations.filename))
            x.start()
            #__write_video__(video_obj,video,annotations)
            json_data.append(video_obj.__dict__)
            file.seek(0)
            json.dump(json_data,file)
    return video_obj

def modify_video(video_obj):
    with lock:
        with open(index_file, "r+") as file:
            json_data=json.load(file)
            for v in json_data:
                if v['name']==video_obj.name:
                    json_data.remove(v)
                    json_data.append(video_obj.__dict__)
                    file.seek(0)
                    file.truncate(0)
                    json.dump(json_data, file)
                    return video_obj

    return None

def set_video_as_processed(video_name):
    obj=None
    with lock:
        with open(index_file, "r+") as file:
            json_data = json.load(file)
            for v in json_data:
                if v['name'] == video_name:
                    v['processed']=True
                    file.seek(0)
                    json.dump(json_data, file)
                    obj=v
                    break;
    return obj

def __write_video__(video_obj,video_dir, video_filename, annotations_filename):

    command = f"ffmpeg -i {video_dir}{video_obj.filename} -preset superfast {video_dir}converted.mp4"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    #process.wait()
    pre=Preprocessor.Preprocessor(video_obj,video_dir, video_filename, f"{video_dir}{annotations_filename}", margin_horizontal=5, margin_vertical=5)
    modify_video(pre.video_obj)
    pre.close()


def save_sprit(path_video,frame_number,id_object,img):
    cv2.imwrite(f"{path_video}{SPRITES_DIR}{os.path.sep}{id_object}{os.path.sep}{frame_number}.jpg",img)
