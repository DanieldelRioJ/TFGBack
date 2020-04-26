import json
import os
import os.path
import threading

import jsonpickle

from helpers import Helper
from io_tools.video import VideoRecorder
from utils.Constants import REPOSITORY_NAME,VIDEOS_FILE,VIDEOS_DIR,SPRITES_DIR
from io_tools.annotations.ParserFactory import ParserFactory
from exceptions.VideoRepeated import VideoRepeated
from exceptions.ObjectNotFound import ObjectNotFound
import subprocess
import cv2

from werkzeug.utils import secure_filename


lock=threading.Lock()

def get_videos():
    with open(get_videos_file_path()) as file:
        j = jsonpickle.decode(file.read())
    return j

def get_video(id):
    with open(get_videos_file_path()) as file:
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
    with open(get_videos_file_path(),'r+') as file:
        file.truncate(0)
        file.write('[]')
    return True

def delete(video_id):
    with open(get_videos_file_path(),'r+') as file:
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
        with open(get_videos_file_path(), "r+") as file:
            json_data = jsonpickle.decode(file.read())
            for v in json_data:
                if v.id == video_obj.id:
                    raise VideoRepeated

            # Save Video
            video.filename = secure_filename(video.filename)
            # .repository/videos/{video_obj.id}/
            video_dir = get_video_base_dir(video_obj)
            os.makedirs(video_dir)
            video.save(os.path.join(video_dir,video.filename))
            annotations.save(os.path.join(video_dir,"gt.txt"))


            json_data.append(video_obj)
            json_data=jsonpickle.encode(json_data)
            file.seek(0)
            file.write(json_data)
    return video_obj

def create_converted_video(video_obj,video_filename):

    __write_video__(get_video_base_dir(video_obj),video_filename,video_obj.fps_adapted)


def modify_video(video_obj):
    with lock:
        with open(get_videos_file_path(), "r+") as file:
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
        with open(get_videos_file_path(), "r+") as file:
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

    command = f"ffmpeg -i {os.path.join(video_dir,video_filename)} -preset ultrafast -r {fps_output} {os.path.join(video_dir,'converted.mp4')}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    #process.wait()


def save_sprite(video_obj, frame_number, object_id, img):
    cv2.imwrite(get_sprite_path(video_obj,object_id,frame_number),img,[cv2.IMWRITE_JPEG_QUALITY, 30])

def get_sprite(video_obj, object_id, frame_number):
    return cv2.imread(get_sprite_path(video_obj,object_id,frame_number))

def get_object_dir(video_obj,obj_id):
    return os.path.join(get_video_base_dir(video_obj),"sprites",str(obj_id))

def get_sprite_path(video_obj, object_id, frame_number):
    return os.path.join(get_object_dir(video_obj,object_id),f"{frame_number}.jpg")

def get_videos_file_path():
    return os.path.join(REPOSITORY_NAME,VIDEOS_FILE)

def get_video_base_dir(video_obj):
    return os.path.join(REPOSITORY_NAME,VIDEOS_DIR,video_obj.id)

def get_background_image(video_obj):
    return cv2.imread(get_background_path(video_obj))

def get_background_path(video_obj):
    return os.path.join(get_video_base_dir(video_obj),"background.jpg")

def get_virtual_video_part_path(video_obj,virtual_id,start):
    return os.path.join(get_virtual_video_base_dir(video_obj,virtual_id),f"{start}.mp4")

def get_virtual_video_heatmap_path(video_obj,virtual_video_id):
    return os.path.join(get_virtual_video_base_dir(video_obj,virtual_video_id),f"heatmap.jpg")

def get_virtual_video_base_dir(video_obj,virtual_id):
    return os.path.join(get_video_base_dir(video_obj),"virtual",virtual_id)

def get_movie_script(video_obj, virtual_id):
    path= os.path.join(get_virtual_video_base_dir(video_obj,virtual_id),"movie_script.json")
    movie_script=None
    with open(path,"r") as file:
        movie_script=jsonpickle.decode(file.read())
    return movie_script

def get_script_list(video_obj, virtual_id, i):
    path=os.path.join(get_virtual_video_base_dir(video_obj,virtual_id),f"{i}.json")
    movie_script=None
    with open(path,"r") as file:
        movie_script=jsonpickle.decode(file.read())
    return movie_script

def save_virtual_video_heatmap(video_obj,virtual_video_id,heatmap):
    cv2.imwrite(get_virtual_video_heatmap_path(video_obj,virtual_video_id),heatmap)

def save_movie_script(video_obj, movie_script, script_lists):
    path = get_virtual_video_base_dir(video_obj,movie_script.id)
    encoded = jsonpickle.encode(movie_script)
    with open(os.path.join(path,"movie_script.json"), "w") as file:
        file.write(encoded)

    i=0
    for script_list in script_lists:
        encoded = jsonpickle.encode(script_list)
        with open(os.path.join(path,f"{i}.json"), "w") as file:
            file.write(encoded)
        i+=1

def get_video_chunk(video_obj,range_header):
    return Helper.get_chunk(get_video_path(video_obj),range_header)

#Returns a chunk of the marked object video
def get_object_video_chunk(video_obj,obj_id,range_header):
    object_directory=os.path.join(get_video_base_dir(video_obj),"sprites",str(obj_id))
    if not os.path.exists(object_directory):
        raise ObjectNotFound
    video_path=os.path.join(object_directory,"alone.mp4")
    if not os.path.exists(video_path):
        v_cv=cv2.VideoCapture(get_video_path(video_obj))

        object_map, _ = get_video_objects(video_obj, adapted=True)
        obj = object_map.get(int(obj_id))
        if obj is None:
            raise ObjectNotFound

        VideoRecorder.generate_individual_video(video_obj,v_cv,obj)
    return Helper.get_chunk(video_path, range_header)

def get_original_video_path(video_obj):
    return os.path.join(get_video_base_dir(video_obj),video_obj.original_filename)

def get_video_path(video_obj):
    return os.path.join(get_video_base_dir(video_obj), "converted.mp4")

def get_gt_adapted_path(video_obj):
    return os.path.join(get_video_base_dir(video_obj), "gt_adapted.txt")

def get_gt_path(video_obj):
    return os.path.join(get_video_base_dir(video_obj),"gt.txt")

#returns the location of the script
def get_script_path(video_obj,movie_script_id):
    return os.path.join(get_video_base_dir(video_obj),"virtual",movie_script_id,"movie_script.json")

#Save background on their path
def save_background(video_obj,background,quality):
    cv2.imwrite(get_background_path(video_obj),background,[cv2.IMWRITE_JPEG_QUALITY, quality])

def save_gt_adapted(video_obj, gt):
    file_path=os.path.join(get_video_base_dir(video_obj),"gt_adapted.txt")
    with open(file_path,"w") as file:
        file.writelines(gt)