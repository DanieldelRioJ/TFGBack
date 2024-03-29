from _json import make_encoder

from flask import Blueprint,request,Response,jsonify,send_file

import os

from io_tools.annotations import MOTParser
from io_tools.data import VideoInfDAO

import datetime
from objects.Video import Video,Perspective
from exceptions.VideoRepeated import VideoRepeated
import time

from virtual_generator import MovieScriptGenerator,MovieScriptGenerator2,VirtualVideoGenerator,HeatMapGenerator
import threading
import jsonpickle
from helpers import PerspectiveHelper
from preprocessor.Preprocessor import Preprocessor

from virtual_generator.filter import FilterQuery



video_controller = Blueprint('video_controller', __name__,url_prefix="/videos")

############# VIDEO DATA ENDPOINTS ###############
@video_controller.route("/",methods=["GET"])
def get_videos():
    video=VideoInfDAO.get_videos()
    response=jsonpickle.encode(video,unpicklable=False)
    return Response(response, 200, mimetype="application/json")

@video_controller.route("",methods=["DELETE"])
def delete_videos():
    return jsonify(VideoInfDAO.deleteAll()),204


def preprocess_video(video_obj,video_filename,chunk_size=None):
    pre=Preprocessor(video_obj,chunk_size)
    VideoInfDAO.create_converted_video(video_obj, video_filename)
    VideoInfDAO.modify_video(pre.video_obj)
    pre.close()

@video_controller.route("",methods=["POST"])
def upload_video():
    req=request
    if 'video' not in request.files:
        print('No file part')
        return "No file part",400
    video = request.files['video']
    annotations = request.files['annotations']

    title=request.form.get("title")
    city = request.form.get("city")
    description = request.form.get("description")
    recorded_date=request.form.get("recorded_date")

    try:
        video_obj=VideoInfDAO.add_video(Video(format(int(time.time() * 1000000),'x'),str(datetime.datetime.now()),
                                              recorded_date,title=title, city=city, description=description,processed=False,original_filename=video.filename),video,annotations)
        preprocess_video(video_obj,video.filename,None)

        return video_obj.__dict__
    except VideoRepeated:
        return "There is already a video with the same videoname",409

@video_controller.route("/<video_name>",methods=["PUT"])
def update_video(video_name):
    video_obj = VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"{video_name} not found", 404

    obj_modified=request.json
    obj_modified['py/object']="objects.Video.Video"
    obj_modified=str(obj_modified).replace("'",'"').replace("True","true").replace("False","false").replace("None","null")
    obj_modified=jsonpickle.decode(obj_modified)
    return jsonpickle.encode(VideoInfDAO.modify_video(obj_modified),unpicklable=True)


@video_controller.route("/<video_name>",methods=["GET"])
def get_video(video_name):

    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"{video_name} not found",404
    return Response(jsonpickle.encode(video_obj,unpicklable=False),200,mimetype="application/json")



@video_controller.route("/<video_name>",methods=["DELETE"])
def delete_video(video_name):
    if VideoInfDAO.delete(video_name) :
        return "",204
    return video_name+" not found",404

########## END VIDEO DATA #############


####### ORIGINAL VIDEO ##############
@video_controller.route('/<video_id>/media')
def get_video_media(video_id:str):

    video_obj=VideoInfDAO.get_video(video_id);

    if video_obj is None:
        return f"{video_id} doesnt exist", 404

    range_header = request.headers.get('Range', None)

    chunk, start, length, file_size = VideoInfDAO.get_video_chunk(video_obj,range_header)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

#################### GET FRAME MAP #########################
@video_controller.route('/<video_name>/frame_map',methods=["GET"])
def get_frame_map(video_name:str):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404
    _, frame_map =VideoInfDAO.get_video_objects(video_obj,adapted=True)
    for k, appearances in frame_map.items():
        for appearance in appearances:
            appearance.object=appearance.object.id
    return jsonpickle.encode(frame_map,unpicklable=False)

#################### VIDEO BACKGROUND ######################
@video_controller.route('/<video_name>/background',methods=["GET"])
def get_background(video_name:str):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    return send_file(VideoInfDAO.get_background_path(video_obj), mimetype="image/jpg")

########### Get objects of video #################
@video_controller.route('/<video_name>/objects',methods=["GET"])
def get_objects(video_name:str):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    object_map, _ =VideoInfDAO.get_video_objects(video_obj,adapted=True)
    for obj_id in object_map:
        obj=object_map[obj_id]
        obj.appearances=None
    return jsonpickle.encode(object_map, unpicklable=False)

################### VIDEO OBJECTS ######################
#GET
@video_controller.route('/<video_name>/objects/<object_id>',methods=["GET"])
def get_object(video_name:str,object_id:int):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    object_map, _ = VideoInfDAO.get_video_objects(video_obj,adapted=True)
    obj=object_map.get(int(object_id))
    if obj is None:
        return f"Object with id: '{object_id}' not found",404
    obj.appearances=None
    return jsonpickle.encode(obj, unpicklable=False)

#Get video containing just the object
@video_controller.route('/<video_name>/objects/<object_id>/video',methods=["GET"])
def get_video_marking_object(video_name:str, object_id:int):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    range_header = request.headers.get('Range', None)

    chunk, start, length, file_size = VideoInfDAO.get_object_video_chunk(video_obj,int(object_id),range_header)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


#Get portrait of object
@video_controller.route('/<video_name>/objects/<object_id>/<frame_number>',methods=["GET"])
def get_object_sprite(video_name:str, object_id:int, frame_number:int):

    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    return send_file(VideoInfDAO.get_sprite_path(video_obj, object_id, frame_number), mimetype="image/jpg")
###################### OBJECT METHODS END #######################


########################## VIRTUAL VIDEO METHODS ############################
#Create virtual video
@video_controller.route('/<video_name>/virtual',methods=["POST"])
def create_virtual_video(video_name:str):
    from controllers.websockets import ProgressSocket

    body=request.json;
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    object_map,frame_map=VideoInfDAO.get_video_objects(video_obj,adapted=True)


    #Notify progress
    ProgressSocket.notify_progress(body['id'],0,'filtering')

    try:
        pixels_per_meter=video_obj.perspective.one_meter if video_obj.perspective!=None else None
    except AttributeError:
        pixels_per_meter = video_obj.perspective.get('one_meter') if video_obj.perspective != None else None
    object_map,group_by_social_distance=FilterQuery.do_filter(object_map,frame_map,body,pixels_per_meter,fps=video_obj.fps_adapted)

    ProgressSocket.notify_progress(body['id'], 30, 'heatmap')
    heatmap = HeatMapGenerator.generate_heatmap(
        [appearance for obj_id in object_map for appearance in object_map.get(obj_id).appearances],
        VideoInfDAO.get_background_image(video_obj))

    # Notify progress
    ProgressSocket.notify_progress(body['id'], 50, 'movie script')

    if group_by_social_distance is None:
        movie_script, script_lists = MovieScriptGenerator.generate_movie_script(object_map.copy(), video_obj)
    else:
        movie_script, script_lists=MovieScriptGenerator2.generate_movie_script(object_map.copy(),group_by_social_distance, video_obj)

    # Notify progress
    ProgressSocket.notify_progress(body['id'], 70, 'saving movie script')

    path_script = VideoInfDAO.get_script_path(video_obj, movie_script.id)
    os.makedirs(os.path.dirname(path_script))
    try:
        encoded=jsonpickle.encode(movie_script,max_depth=3)
    except RecursionError:
        passwf
    VideoInfDAO.save_movie_script(video_obj,movie_script,script_lists)
    VideoInfDAO.save_virtual_video_heatmap(video_obj,movie_script.id,heatmap)
    # Notify progress
    ProgressSocket.notify_progress(body['id'], 100, 'Downloading')
    return Response(encoded,201,mimetype="application/json")

############################ VIDEO HEATMAP###################
@video_controller.route('/<video_name>/virtual/<virtual_id>/heatmap',methods=["GET"])
def get_virtual_video_heatmap(video_name:str,virtual_id:str):
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    return send_file(VideoInfDAO.get_virtual_video_heatmap_path(video_obj,virtual_id), mimetype="image/jpg")

#Get part of virtual video
@video_controller.route('/<video_name>/virtual/<virtual_id>/<movie_part>',methods=["GET"])
def get_movie_script_part(video_name:str,virtual_id:str,movie_part:int):
    movie_part=int(movie_part)
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404
    movie_script_part=VideoInfDAO.get_script_list(video_obj,virtual_id,movie_part)
    for frame in movie_script_part:
        for appearance in frame.appearance_list:
            appearance.object=appearance.object.id
    return jsonpickle.encode(movie_script_part,unpicklable=False)

#Get part of virtual video
@video_controller.route('/<video_name>/virtual/<virtual_id>',methods=["GET"])
def get_virtual_video_part(video_name:str, virtual_id:str):
    print("start")
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

###################### VIRTUAL VIDEO METHODS END ###################################

###################### VIDEO PERSPECTIVE #################################
#Create virtual video
@video_controller.route('/<video_name>/perspective',methods=["POST"])
def add_perspective_points(video_name:str):
    print("PERSPECTIVE")
    body=request.json
    points=body.get('points')
    ratio=body.get('ratio')
    references=body.get('references')
    video_obj=VideoInfDAO.get_video(video_name)
    if video_obj is None:
        return f"Video {video_name} does not exists",404

    object_map, frame_map = VideoInfDAO.get_video_objects(video_obj, adapted=True)
    if points is not None:
        points = [(point['x'], point['y']) for point in points]

        object_map,upper_left_limit,lower_left_limit, one_meter,converted_references=PerspectiveHelper.add_real_coordinates(points,object_map,references,ratio,video_obj.fps_adapted)

        video_obj.perspective=Perspective(upper_left_limit,lower_left_limit,points, one_meter, references,converted_references,ratio=ratio)
        video = VideoInfDAO.modify_video(video_obj)
        VideoInfDAO.save_gt_adapted(video_obj, MOTParser.parse_back(frame_map, object_map))
    else:
        video_obj.perspective=None
        video=VideoInfDAO.modify_video(video_obj)
        VideoInfDAO.save_gt_adapted(video, MOTParser.parse_back(frame_map, object_map))
    return Response(jsonpickle.encode(video,unpicklable=False),200,mimetype="application/json")



