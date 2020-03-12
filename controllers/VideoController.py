from flask import Blueprint,request,Response,jsonify
import re
import os
from io_tools.data import VideoInfDAO
import datetime
from objects.Video import Video
from exceptions.VideoRepeated import VideoRepeated

video_controller = Blueprint('video_controller', __name__,url_prefix="/videos")


@video_controller.route("/",methods=["GET"])
def get_videos():
    return jsonify(VideoInfDAO.get_video_index())

"""@video_controller.route("/<video_name>",methods=["GET"])
def get_video(video_name):
    return jsonify(VideoInfDAO.get_video(video_name))"""

@video_controller.route("/",methods=["DELETE"])
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

@video_controller.route('/<video_name>')
def get_video_media(video_name:str):
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(video_name,byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

@video_controller.route("",methods=["POST"])
def upload_video():
    if 'video' not in request.files:
        print('No file part')
        return "No file part",400
    video = request.files['video']
    annotations = request.files['annotations']

    try:
        video_name=video.filename+str(datetime.datetime.now()).replace(" ","_")
        return VideoInfDAO.add_video(Video(video_name,video.filename,annotations.filename,str(datetime.datetime.now()),str(datetime.datetime.now()),-1,-1,-1),video,annotations).__dict__
    except VideoRepeated:
        return "There is already a video with the same videoname",409
