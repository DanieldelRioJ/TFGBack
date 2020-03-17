from flask import Blueprint,request,Response,jsonify

query_controller = Blueprint('query_controller', __name__,url_prefix="/videos/virtual")

@query_controller.route("",methods=["POST"])
def create_virtual_video(query_filter_params):
    print("Hola jeje")
    pass