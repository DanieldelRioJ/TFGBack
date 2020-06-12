from app import socketio,app
from controllers.websockets.ProgressSocket import *

if __name__ == '__main__':
    socketio.run(app,debug=False,host='0.0.0.0')
