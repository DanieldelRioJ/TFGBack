from flask import Blueprint,request,Response
import re
import os
from io_tools.data import VideoInfDAO
import datetime
from objects import Video
from exceptions import VideoRepeated

video_controller = Blueprint('video_controller', __name__,url_prefix="/video")

@video_controller.route("",methods=["POST"])
def upload_video():
    if 'video' not in request.files:
        print('No file part')
        return "No file part",400
    video = request.files['video']
    annotations = request.files['annotations']

    try:
        VideoInfDAO.add_video(Video.get_video_instance(video.filename,annotations.filename,str(datetime.datetime.now()),str(datetime.datetime.now()),69,5000,25),video,annotations)
    except VideoRepeated:
        return "There is already a video with the same videoname",409

    print(request.form.get("texto"))
    return video.filename

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
def video(video_name:str):
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