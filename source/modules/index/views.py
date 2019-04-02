from . import index_blueprint
from flask import session,request,make_response
from source import redis_store     # try to use the redis_store here, not a must, depending the request logic

@index_blueprint.route('/')
def HomeTestPage():
    session['username']="savor"
    session['password']="test"
    redis_store.set("test","onging")
    return make_response("Welcome to Home Test Page!")