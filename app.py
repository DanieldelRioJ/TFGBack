from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from controllers import VideoController,QueryController



app = Flask(__name__)
app.register_blueprint(VideoController.video_controller)
app.register_blueprint(QueryController.query_controller)


socketio=SocketIO(app,cors_allowed_origins="*",engineio_logger=True)
cors = CORS(app, resources={r"/*": {"origins": "*"}})