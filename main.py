from preprocessor.Preprocessor import Preprocessor

from controllers import VideoController
from flask import Flask,jsonify,request,send_file,make_response,Response
from flask_cors import CORS
app = Flask(__name__)
app.register_blueprint(VideoController.video_controller)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def main():
    try:
        preprocessor=Preprocessor("./data/17/video.mp4","./data/17/gt.txt",100,0,0)
        preprocessor = Preprocessor("./data/15/kitty/video.mp4", "./data/15/kitty/gt.txt", 100, 0, 0)
        preprocessor = Preprocessor("./data/15/venice/video.mp4", "./data/15/venice/gt.txt", 30, 0, 0,block_size=10)
    except FileNotFoundError:
        print("File not found")
    pass

if __name__ == '__main__':
    main()
    app.run(debug=False,threaded=True)