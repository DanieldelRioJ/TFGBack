import datetime

from preprocessor.Preprocessor import Preprocessor

from io_tools.data.DataSchemeCreator import setup
from io_tools.data import VideoInfDAO

from objects import Video

from controllers import VideoController
from flask import Flask,jsonify,request,send_file,make_response,Response
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(VideoController.video_controller)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def main():
    try:
        #preprocessor=Preprocessor("./data/17/","video.mp4","./data/17/gt.txt").close()
        preprocessor = Preprocessor("./data/15/easy/","video.mp4", "./data/15/easy/gt.txt",margin_horizontal=10,margin_vertical=10).close()
        """preprocessor = Preprocessor("./data/15/adl/","video.mp4", "./data/15/adl/gt.txt").close()
        preprocessor = Preprocessor("./data/15/tud/","video.mp4", "./data/15/tud/gt.txt",margin_horizontal=5,margin_vertical=5).close()
        preprocessor = Preprocessor("./data/15/kitty/","video.mp4", "./data/15/kitty/gt.txt",margin_horizontal=5,margin_vertical=5).close()
        preprocessor = Preprocessor("./data/15/venice/","video.mp4", "./data/15/venice/gt.txt",margin_horizontal=5,margin_vertical=5).close()"""

    except FileNotFoundError:
        print("File not found")
    pass

if __name__ == '__main__':
    setup()
    #VideoInfDAO.add_video(Video.get_video_instance("video1",str(datetime.datetime.now()),str(datetime.datetime.now()),69,5000,25))
    #VideoInfDAO.add_video(Video.get_video_instance("video2", str(datetime.datetime.now()), str(datetime.datetime.now()), 69, 5000, 25))

    #main()
    app.run(debug=False,threaded=True)
