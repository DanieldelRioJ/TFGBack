from controllers import VideoController
from flask import Flask,jsonify,request,send_file,make_response,Response
from flask_cors import CORS
app = Flask(__name__)
app.register_blueprint(VideoController.video_controller)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=False,threaded=True)