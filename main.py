import datetime

from preprocessor.Preprocessor import Preprocessor

from io_tools.data.DataSchemeCreator import setup
from io_tools.data import VideoInfDAO
from io_tools.annotations.ParserFactory import ParserFactory
from objects import Video

from controllers import VideoController
from flask import Flask,jsonify,request,send_file,make_response,Response
from flask_cors import CORS

import cv2
import os

app = Flask(__name__)
app.register_blueprint(VideoController.video_controller)
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

        video_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/17/video.mp4"
        annotations_file = "/home/pankratium/Documentos/Universidad/4/TFG/Code/BackEnd/data/17/gt.txt"
        objects,frame_dict=ParserFactory.get_parser(annotations_file).parse(remove_static_objects=True,iou_limit=0.8,static_porcentage_time=0.9)
        video = cv2.VideoCapture(video_file)
        ok = True
        i=1
        while (ok):
            ok, img = video.read()
            if not ok:
                break
            if  frame_dict.get(i) != None:
                for appearance in frame_dict.get(i):
                    img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                        pt2=(appearance.col + appearance.w, appearance.row + appearance.h),
                                        color=(0, 0, 255),
                                        thickness=1)
            cv2.namedWindow('detection', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('detection', 900, 600)
            cv2.imshow("detection", img)
            cv2.waitKey(1)
            i+=1

    except FileNotFoundError:
        print("File not found")
    pass

if __name__ == '__main__':
    setup()
    #VideoInfDAO.add_video(Video.get_video_instance("video1",str(datetime.datetime.now()),str(datetime.datetime.now()),69,5000,25))
    #VideoInfDAO.add_video(Video.get_video_instance("video2", str(datetime.datetime.now()), str(datetime.datetime.now()), 69, 5000, 25))

    main()
    #app.run(debug=True,threaded=True,host='0.0.0.0')
