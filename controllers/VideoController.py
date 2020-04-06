from flask import Blueprint,request,Response,jsonify,send_file
import re
import os
from io_tools.data import VideoInfDAO
from io_tools.annotations.ParserFactory import ParserFactory
import datetime
from objects.Video import Video
from exceptions.VideoRepeated import VideoRepeated
import time
from utils.Constants import REPOSITORY_NAME,VIDEOS_DIR,SPRITES_DIR
from video_generator import MovieScriptGenerator,VirtualVideoGenerator
import threading
import jsonpickle
from preprocessor.Preprocessor import Preprocessor
from video_generator.filter.Filter import Filter
from video_generator.filter import FilterQuery

video_controller = Blueprint('video_controller', __name__,url_prefix="/videos")


@video_controller.route("/",methods=["GET"])
def get_videos():
    return Response(jsonpickle.encode(VideoInfDAO.get_video_index()),200,mimetype="application/json")


@video_controller.route("/<video_name>",methods=["GET"])
def get_video(video_name):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"{video_name} not found",404
    return Response(jsonpickle.encode(video_obj),200,mimetype="application/json")

@video_controller.route("",methods=["DELETE"])
def delete_videos():
    return jsonify(VideoInfDAO.deleteAll()),204

@video_controller.route("/<video_name>",methods=["DELETE"])
def delete_video(video_name):
    if VideoInfDAO.delete(video_name) :
        return "",204
    return video_name+" not found",404

def get_chunk(full_path,byte1=None, byte2=None):
    file_size = os.stat(full_path).st_size
    start = 0
    length = 102400

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size

@video_controller.route('/<video_id>/media')
def get_video_media(video_id:str):

    video_obj=VideoInfDAO.get_video(video_id);

    if video_obj is None:
        return f"{video_id} doesnt exist", 404

    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    video_path,_,_=VideoInfDAO.get_paths(video_obj)
    chunk, start, length, file_size = get_chunk(video_path,byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


#Get part of virtual video
@video_controller.route('/<video_name>/background',methods=["GET"])
def get_background(video_name:str):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    return send_file(VideoInfDAO.get_background(video_obj),mimetype="image/jpg")

#Create virtual video
@video_controller.route('/<video_name>/virtual',methods=["POST"])
def create_virtual_video(video_name:str):
    body=request.json;
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    path_video, path_gt,_=VideoInfDAO.get_paths(video_obj)
    path_gt=VideoInfDAO.get_gt_adapted_path(video_obj)
    object_map,frame_map=ParserFactory.get_parser(path_gt).parse(remove_static_objects=False)

    object_map=FilterQuery.do_filter(object_map,body,fps=video_obj.fps_adapted)
    movie_script=MovieScriptGenerator.generate_movie_script(object_map)
    path_script = VideoInfDAO.get_script_path(video_obj, movie_script.id)
    os.makedirs(os.path.dirname(path_script))

    encoded=jsonpickle.encode(movie_script)
    with open(path_script,"w") as file:
        file.write(encoded)
    return Response(encoded,200,mimetype="application/json")

#Get part of virtual video
@video_controller.route('/<video_name>/virtual/<virtual_id>',methods=["GET"])
def get_part_virtual_video(video_name:str,virtual_id:str):
    print("start")
    start=None
    start=request.args.get('start')
    if start is None:
        start=0
    else:
        start=int(start)
    print("Getting video data")
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404
    print("Getting movie script")
    movie_script=VideoInfDAO.get_movie_script(video_obj,virtual_id)
    print("Generating virtual video")
    video_path=VirtualVideoGenerator.generate_virtual_video(video_obj,movie_script,start)
    print("Video generated")
    return send_file(video_path,mimetype="video/mp4")

def preprocess_video(video_obj,chunk_size=None):
    pre=Preprocessor(video_obj,chunk_size)
    VideoInfDAO.modify_video(pre.video_obj)
    pre.close()


@video_controller.route("",methods=["POST"])
def upload_video():
    if 'video' not in request.files:
        print('No file part')
        return "No file part",400
    video = request.files['video']
    annotations = request.files['annotations']

    title=request.form.get("title")
    city = request.form.get("city")
    description = request.form.get("description")

    try:
        video_name=video.filename+str(datetime.datetime.now()).replace(" ","_")
        video_obj=VideoInfDAO.add_video(Video(format(int(time.time() * 1000000),'x'),str(datetime.datetime.now()),
                                              str(datetime.datetime.now()),title=title, city=city, description=description,processed=False),video,annotations)
        x = threading.Thread(target=preprocess_video,
                             args=(video_obj,None))
        x.start()

        return video_obj.__dict__
    except VideoRepeated:
        return "There is already a video with the same videoname",409

