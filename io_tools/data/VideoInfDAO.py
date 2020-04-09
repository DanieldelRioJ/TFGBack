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

def get_video(id):
    with open(index_file) as file:
        json_data=jsonpickle.decode(file.read())
        for v in json_data:
            if v.id==id:
                return v
    return None

def deleteAll():
    with open(index_file,'r+') as file:
        file.truncate(0)
        file.write('[]')
    return True

def delete(video_id):
    with open(index_file,'r+') as file:
        json_data = json.load(file)
        for v in json_data:
            if v['id'] == video_id:
                json_data.remove(v)
                file.seek(0)
                file.truncate(0)
                json.dump(json_data,file)
                return True
    return False

def add_video(video_obj, video, annotations):
    with lock:
        with open(index_file, "r+") as file:
            json_data = jsonpickle.decode(file.read())
            for v in json_data:
                if v.id == video_obj.id:
                    raise VideoRepeated

            # Save Video
            video.filename = secure_filename(video.filename)

            # .repository/videos/{video_obj.id}/
            video_dir = f"{REPOSITORY_NAME}{bar}{VIDEOS_DIR}{bar}{video_obj.id}{bar}"
            os.makedirs(video_dir)
            video.save(video_dir + video.filename)
            annotations.save(video_dir + "gt.txt")

            x = threading.Thread(target=__write_video__,
                                 args=(video_dir,video.filename))
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
                if v.id==video_obj.id:
                    json_data.remove(v)
                    json_data.append(video_obj)
                    json_data = jsonpickle.encode(json_data)
                    file.seek(0)
                    file.truncate(0)
                    file.write(json_data)
                    return video_obj

    return None

def set_video_as_processed(video_id):
    obj=None
    with lock:
        with open(index_file, "r+") as file:
            json_data = jsonpickle.decode(file.read())
            for v in json_data:
                if v.id == video_id:
                    v.name=True
                    file.seek(0)
                    file.write(jsonpickle.encode(json_data))
                    obj=v
                    break;
    return obj

def __write_video__(video_dir, video_filename):

    command = f"ffmpeg -i {video_dir}{video_filename} -preset ultrafast {video_dir}converted.mp4"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    #process.wait()


def save_sprit(path_video,frame_number,id_object,img):
    cv2.imwrite(f"{path_video}{SPRITES_DIR}{os.path.sep}{id_object}{os.path.sep}{frame_number}.jpg",img,[cv2.IMWRITE_JPEG_QUALITY, 30])

def get_sprit(video_obj,object_id,frame_number):
    return cv2.imread(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/{SPRITES_DIR}/{object_id}/{frame_number}.jpg")

def get_sprit_path(video_obj,object_id,frame_number):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/{SPRITES_DIR}/{object_id}/{frame_number}.jpg"


def get_background(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg"

def get_movie_script(video_obj, virtual_id):
    path= f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{virtual_id}/movie_script.json"
    movie_script=None
    with open(path,"r") as file:
        movie_script=jsonpickle.decode(file.read())
    return movie_script

def get_script_list(video_obj, virtual_id, i):
    path= f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{virtual_id}/{i}.json"
    movie_script=None
    with open(path,"r") as file:
        movie_script=jsonpickle.decode(file.read())
    return movie_script

def save_movie_script(video_obj, movie_script, script_lists):
    path = f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{movie_script.id}/"
    encoded = jsonpickle.encode(movie_script)
    with open(path+"movie_script.json", "w") as file:
        file.write(encoded)

    i=0
    for script_list in script_lists:
        encoded = jsonpickle.encode(script_list)
        with open(path + f"{i}.json", "w") as file:
            file.write(encoded)
        i+=1

def get_paths(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/converted.mp4"\
        ,f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt.txt"\
        ,f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg"

def get_gt_adapted_path(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt_adapted.txt"

def get_script_path(video_obj,movie_script_id):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{movie_script_id}/movie_script.json"

def save_background(video_obj,background,quality):
    cv2.imwrite(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg",background,[cv2.IMWRITE_JPEG_QUALITY, quality])

def save_gt_adapted(video_obj, gt):
    file_path=f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt_adapted.txt"
    with open(file_path,"w") as file:
        file.writelines(gt)