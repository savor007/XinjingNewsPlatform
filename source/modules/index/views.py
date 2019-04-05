from . import index_blueprint
from flask import url_for,session,request,make_response, render_template,redirect
from source import redis_store     # try to use the redis_store here, not a must, depending the request logic

@index_blueprint.route('/')
def HomeTestPage():
    # session['username']="savor"
    # session['password']="test"
    # redis_store.set("test","onging")
    return render_template('news/index.html')


@index_blueprint.route('/index.html')
def HomeIndexPage():
    return redirect(url_for('index.HomeTestPage'))