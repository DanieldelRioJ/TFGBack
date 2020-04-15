import json
import os
import threading

import jsonpickle

from helpers import Helper
from io_tools.video import VideoRecorder
from utils.Constants import REPOSITORY_NAME,VIDEOS_FILE,VIDEOS_DIR,SPRITES_DIR
from io_tools.annotations.ParserFactory import ParserFactory
from exceptions.VideoRepeated import VideoRepeated
from exceptions.ObjectNotFound import ObjectNotFound
from preprocessor import Preprocessor
import subprocess
import cv2

from werkzeug.utils import secure_filename

from virtual_generator import VirtualVideoGenerator

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

def get_video_objects(video_obj, adapted=False,remove_static_objects=False):
    if adapted:
        path_gt = get_gt_adapted_path(video_obj)
    else:
        path_gt=get_gt_path(video_obj)
    return ParserFactory.get_parser(path_gt).parse(remove_static_objects=remove_static_objects)

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


            json_data.append(video_obj)
            json_data=jsonpickle.encode(json_data)
            file.seek(0)
            file.write(json_data)
    return video_obj

def create_converted_video(video_obj,video_filename):

    __write_video__(get_video_base_dir(video_obj),video_filename,video_obj.fps_adapted)


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

def __write_video__(video_dir,video_filename,fps_output):

    command = f"ffmpeg -i {video_dir}{video_filename} -preset ultrafast -r {fps_output} {video_dir}converted.mp4"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    #process.wait()


def save_sprit(path_video,frame_number,id_object,img):
    cv2.imwrite(f"{path_video}{SPRITES_DIR}{os.path.sep}{id_object}{os.path.sep}{frame_number}.jpg",img,[cv2.IMWRITE_JPEG_QUALITY, 30])

def get_sprit(video_obj,object_id,frame_number):
    return cv2.imread(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/{SPRITES_DIR}/{object_id}/{frame_number}.jpg")

def get_sprit_path(video_obj,object_id,frame_number):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/{SPRITES_DIR}/{object_id}/{frame_number}.jpg"

def get_video_base_dir(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/"

def get_background_image(video_obj):
    return cv2.imread(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg")

def get_background_path(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg"

def get_virtual_video_heatmap_path(video_obj,virtual_video_id):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{virtual_video_id}/heatmap.jpg"

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

def save_virtual_video_heatmap(video_obj,virtual_video_id,heatmap):
    cv2.imwrite(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{virtual_video_id}/heatmap.jpg",heatmap)

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

def get_video_chunk(video_obj,range_header):
    return Helper.get_chunk(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/converted.mp4",range_header)

def get_object_video_chunk(video_obj,obj_id,range_header):
    object_directory=f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/sprites/{obj_id}/"
    if not os.path.exists(object_directory):
        raise ObjectNotFound
    video_path=f"{object_directory}alone.mp4"
    if not os.path.exists(video_path):
        v_cv=cv2.VideoCapture(get_video_path(video_obj))

        object_map, _ = get_video_objects(video_obj, adapted=True)
        obj = object_map.get(int(obj_id))
        if obj is None:
            raise ObjectNotFound

        VideoRecorder.generate_individual_video(video_obj,v_cv,obj)
    return Helper.get_chunk(video_path, range_header)

def get_paths(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/converted.mp4"\
        ,f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt.txt"\
        ,f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg"

def get_original_video_path(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/video.mp4"

def get_video_path(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/converted.mp4"

def get_gt_adapted_path(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt_adapted.txt"

def get_gt_path(video_obj):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt.txt"

def get_script_path(video_obj,movie_script_id):
    return f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/virtual/{movie_script_id}/movie_script.json"

def save_background(video_obj,background,quality):
    cv2.imwrite(f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/background.jpg",background,[cv2.IMWRITE_JPEG_QUALITY, quality])

def save_gt_adapted(video_obj, gt):
    file_path=f"{REPOSITORY_NAME}/{VIDEOS_DIR}/{video_obj.id}/gt_adapted.txt"
    with open(file_path,"w") as file:
        file.writelines(gt)