from app import socketio,app
from flask_socketio import emit,join_room,leave_room
def __get_virtual_video_room_name__(virtual_id):
    return "virtual-"+virtual_id

def notify_progress(virtual_id, progress, step):
    print(f"sending {progress} {step}")
    socketio.sleep(0)
    socketio.emit("progress", {"virtual_id": virtual_id, "progress": progress, "step":step},
                  room=__get_virtual_video_room_name__(virtual_id), namespace="/virtual")

@socketio.on("subscribe",namespace="/virtual")
def subscribe(virtual_id):
    print("Subscribed to virtual video:" + virtual_id)
    room="virtual-" + virtual_id
    join_room(room)
    return {"virtual":virtual_id, "message": f"Subscribed to virtual video {virtual_id} progress"}