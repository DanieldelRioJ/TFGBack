import json
import os
import threading

import jsonpickle

from utils.Constants import REPOSITORY_NAME,VIDEOS_FILE,VIDEOS_DIR,SPRITES_DIR
from exceptions.VideoRepeated import VideoRepeated
from preprocessor import Preprocessor
import subprocess
import cv2

from werkzeug.utils import secure_filename

lock=threading.Lock()
bar=os.path.sep

#.repository/videos.json
index_file=f"{REPOSITORY_NAME}{bar}{VIDEOS_FILE}"

def get_video_index():
    with open(index_file) as file:
        j = jsonpickle.decode(file.read())
    return j

def get_video(name):
    with open(index_file) as file:
        json_data=jsonpickle.decode(file.read())
        for v in json_data:
            if v.name==name:
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
    """with lock:
        with open(index_file,"r+") as file:
            json_data=json.load(file)
            for v in json_data:
                if v['name']==video_obj.name:
                    raise VideoRepeated

            #Save Video
            video.filename = secure_filename(video.filename)
            annotations.filename = secure_filename(annotations.filename)

            #.repository/videos/{video_obj.name}/
            video_dir = f"{REPOSITORY_NAME}{bar}{VIDEOS_DIR}{bar}{video_obj.name}{bar}"
            os.makedirs(video_dir)
            video.save(video_dir + video_obj.filename)
            annotations.save(video_dir + annotations.filename)

            x = threading.Thread(target=__write_video__, args=(video_obj,video_dir,video.filename,annotations.filename))
            x.start()
            #__write_video__(video_obj,video,annotations)
            json_data.append(video_obj.__dict__)
            file.seek(0)
            json.dump(json_data,file)
    return video_obj"""
    with lock:
        with open(index_file, "r+") as file:
            json_data = jsonpickle.decode(file.read())
            for v in json_data:
                if v.name == video_obj.name:
                    raise VideoRepeated

            # Save Video
            video.filename = secure_filename(video.filename)
            annotations.filename = secure_filename(annotations.filename)

            # .repository/videos/{video_obj.name}/
            video_dir = f"{REPOSITORY_NAME}{bar}{VIDEOS_DIR}{bar}{video_obj.name}{bar}"
            os.makedirs(video_dir)
            video.save(video_dir + video_obj.filename)
            annotations.save(video_dir + annotations.filename)

            x = threading.Thread(target=__write_video__,
                                 args=(video_obj, video_dir, video.filename, annotations.filename))
            x.start()
            # __write_video__(video_obj,video,annotations)
            json_data.append(video_obj)
            json_data=jsonpickle.encode(json_data)
            file.seek(0)
            file.write(json_data)
    return video_obj

def modify_video(video_obj):
    with lock:
        with open(index_file, "r+") as file:
            json_data=jsonpickle.decode(file.read())
            for v in json_data:
                if v.name==video_obj.name:
                    json_data.remove(v)
                    json_data.append(video_obj)
                    json_data = jsonpickle.encode(json_data)
                    file.seek(0)
                    file.truncate(0)
                    file.write(json_data)
                    return video_obj

    return None

def set_video_as_processed(video_name):
    obj=None
    with lock:
        with open(index_file, "r+") as file:
            json_data = jsonpickle.decode(file.read())
            for v in json_data:
                if v.name == video_name:
                    v.name=True
                    file.seek(0)
                    file.write(jsonpickle.encode(json_data))
                    obj=v
                    break;
    return obj

def __write_video__(video_obj,video_dir, video_filename, annotations_filename):

    command = f"ffmpeg -i {video_dir}{video_obj.filename} -preset superfast {video_dir}converted.mp4"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    #process.wait()
    """pre = Preprocessor.Preprocessor(video_obj, video_dir, video_filename, f"{video_dir}{annotations_filename}",
                                    margin_horizontal=5, margin_vertical=5)
    modify_video(pre.video_obj)
    pre.close()"""


def save_sprit(path_video,frame_number,id_object,img):
    cv2.imwrite(f"{path_video}{SPRITES_DIR}{os.path.sep}{id_object}{os.path.sep}{frame_number}.jpg",img)

def get_sprit(video_obj,object_id,frame_number):
    return cv2.imread(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.name}/{SPRITES_DIR}/{object_id}/{frame_number}.jpg")

def get_movie_script(video_obj, virtual_id):
    path= f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.name}/virtual/{virtual_id}/movie_script.json"
    movie_script=None
    with open(path,"r") as file:
        movie_script=jsonpickle.decode(file.read())
    return movie_script

def get_paths(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.name}/{video_obj.filename}"\
        ,f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.name}/{video_obj.annotations_filename}"\
        ,f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.name}/background.jpg"

def get_script_path(video_obj,movie_script_id):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.name}/virtual/{movie_script_id}/movie_script.json"