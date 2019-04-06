from . import passport_blueprint
from source.constants import *
from flask import jsonify, request, make_response



@passport_blueprint.route('/', methods=['POST'])
def SMSVerfification():
    pass



@passport_blueprint.route('/', methods=['GET'])
def GetVerficationImage():
    pass
