import datetime
import pickle
import jsonpickle

from preprocessor.Preprocessor import Preprocessor

from io_tools.data.DataSchemeCreator import setup
from io_tools.data import VideoInfDAO
from io_tools.annotations.ParserFactory import ParserFactory
from objects import Video
from video_generator import MovieScriptGenerator

import json

from video_generator.filter import FilterQuery,ColorFilter,TimeFilter

from controllers import VideoController
from controllers import QueryController
from flask import Flask,jsonify,request,send_file,make_response,Response
from flask_cors import CORS

import cv2
import os
import numpy as np

app = Flask(__name__)
app.register_blueprint(VideoController.video_controller)
app.register_blueprint(QueryController.query_controller)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def main():
    try:
        #preprocessor=Preprocessor("./data/17/","video.mp4","./data/17/gt.txt").close()
        #preprocessor = Preprocessor("./data/15/easy/","video.mp4", "./data/15/easy/gt.txt",margin_horizontal=10,margin_vertical=10).close()
        """preprocessor = Preprocessor("./data/15/adl/","video.mp4", "./data/15/adl/gt.txt").close()
        preprocessor = Preprocessor("./data/15/tud/","video.mp4", "./data/15/tud/gt.txt",margin_horizontal=5,margin_vertical=5).close()
        preprocessor = Preprocessor("./data/15/kitty/","video.mp4", "./data/15/kitty/gt.txt",margin_horizontal=5,margin_vertical=5).close()
        preprocessor = Preprocessor("./data/15/venice/","video.mp4", "./data/15/venice/gt.txt",margin_horizontal=5,margin_vertical=5).close()"""

        lower_body=cv2.CascadeClassifier('haarcascade/haarcascade_lowerbody.xml')
        path="/home/pankratium/Documentos/Universidad/4º/TFG/Code/BackEnd/.repository/videos/video.mp42020-03-06_23:28:18.588983/sprites/15/"


        """lista_nombres_imagen=os.listdir(path)
        lista_nombres_imagen.sort()
        for img_name in lista_nombres_imagen:
            img=cv2.imread(path+img_name)
            grey=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            lowers=lower_body.detectMultiScale(grey)
            for (x,y,w,h) in lowers:
                img=cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                print("yeah")
            cv2.imshow("detection",img)
            cv2.waitKey()"""

        """video_file="/home/pankratium/Documentos/Universidad/4º/TFG/Code/BackEnd/data/15/easy/video.mp4"
        video=cv2.VideoCapture(video_file)
        ok=True
        while(ok):
            ok,img = video.read()
            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            lowers = lower_body.detectMultiScale(grey)
            for (x, y, w, h) in lowers:
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                print("yeah")
            cv2.imshow("detection", img)
            cv2.waitKey()"""

    except FileNotFoundError:
        print("File not found")
    pass

def create_background():
    video_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/17/video.mp4"
    backSub = cv2.createBackgroundSubtractorKNN()
    video = cv2.VideoCapture(video_file)
    while True:
        ret, frame = video.read()
        if frame is None:
            break
        fgMask = backSub.apply(frame)
        rest,fgMask=cv2.threshold(fgMask,127,255,cv2.THRESH_BINARY)
        res= cv2.bitwise_and(frame,frame,mask = 255-fgMask)
        cv2.namedWindow('detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('detection', 900, 600)
        cv2.imshow("detection", res)
        cv2.waitKey(1)


def show_iou():
    video_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/17/video.mp4"
    annotations_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/17/gt.txt"
    """video_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/15/easy/video.mp4"
    annotations_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/15/easy/gt.txt" """
    objects, frame_dict = ParserFactory.get_parser(annotations_file).parse(remove_static_objects=True, iou_limit=0.99,
                                                                           static_porcentage_time=0.99)
    video = cv2.VideoCapture(video_file)
    ok = True
    i = 1
    while (ok):
        ok, img = video.read()
        if not ok:
            break
        if frame_dict.get(i) != None:
            for appearance in frame_dict.get(i):
                img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                    pt2=(appearance.col + appearance.w, appearance.row + appearance.h),
                                    color=appearance.object.color,
                                    thickness=2)
                img = cv2.putText(img, str(appearance.object.id), (appearance.col, appearance.row),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                img = cv2.putText(img, str(round(appearance.iou, 3)), (appearance.col, appearance.row + 20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        cv2.namedWindow('detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('detection', 900, 600)
        cv2.imshow("detection", img)
        cv2.waitKey(1)
        i += 1


def generate_movie_script():
    path="/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/.repository/videos/5a0ffb3722c6e/"
    annotations_file = path+"gt.txt"
    background=cv2.imread(path+"background.jpg")
    #annotations_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/15/easy/gt.txt"
    objects, frame_dict = ParserFactory.get_parser(annotations_file).parse(remove_static_objects=True, iou_limit=0.99,
                                                                           static_porcentage_time=0.99)
    video=VideoInfDAO.get_video("5a0ffb3722c6e")


    objects=FilterQuery.FilterQuery().do_filter(objects,time_filter=TimeFilter.TimeFilter(0,1,"frames"),fps=video.fps)
    x=MovieScriptGenerator.generate_movie_script(objects)

    i=1
    for frame in x:
        img=background.copy()
        for appearance in frame.appearance_list:
            sprite=cv2.imread(f"{path}sprites/{appearance.object.id}/{appearance.frame}.jpg")
            aux=img[appearance.row:appearance.row+appearance.h, appearance.col:appearance.col+appearance.w]
            if appearance.overlapped:
                sprite=cv2.addWeighted(sprite, 0.5, aux, 0.5, 0.0)
                #sprite=cv2.scaleAdd(sprite,0.5,aux)
            img[appearance.row:appearance.row + appearance.h, appearance.col:appearance.col + appearance.w]=sprite
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=appearance.object.color,
                                thickness=1)
            img = cv2.putText(img, str(appearance.object.id), (appearance.col, appearance.row),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
            img = cv2.putText(img, str(datetime.timedelta(seconds=appearance.frame/7)).split(".")[0], (appearance.col, appearance.row+20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
            img = cv2.putText(img, str(appearance.overlapped), (appearance.col, appearance.row+40),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))
        img=cv2.putText(img, str(i), (0, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        cv2.imshow("script",img)
        cv2.waitKey(100)
        i+=1


if __name__ == '__main__':
    #setup()
    #VideoInfDAO.add_video(Video.get_video_instance("video1",str(datetime.datetime.now()),str(datetime.datetime.now()),69,5000,25))
    #VideoInfDAO.add_video(Video.get_video_instance("video2", str(datetime.datetime.now()), str(datetime.datetime.now()), 69, 5000, 25))
    #create_background()
    #main()
    #generate_movie_script()
    #app.run(debug=True,threaded=True,host='0.0.0.0')
    VideoController.get_part_virtual_video("5a126d3f7686a","5a19972c39875")

"""import hashlib
import datetime
import time

print(format(int(time.time() * 1000000),'x'))"""