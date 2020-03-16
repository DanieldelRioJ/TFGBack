from flask import Blueprint,request,Response,jsonify

query_controller = Blueprint('query_controller', __name__,url_prefix="/videos/virtual")