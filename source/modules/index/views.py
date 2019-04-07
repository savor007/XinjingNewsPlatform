from source.utility.response_code import RET
from . import index_blueprint
from flask import url_for,session,request,make_response, render_template,redirect,current_app, jsonify
from source import redis_store, NewsDB  # try to use the redis_store here, not a must, depending the request logic
from source.models import *

@index_blueprint.route('/')
def HomeTestPage():
    user_id=session.get('user_id')
    # session['password']="test"
    # redis_store.set("test","onging")
    user=None
    if user_id:    #  user already log in
        try:
            user=User.query.filter(User.id==user_id).first()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="dabase access erroor when search user avatar.")
    if user:
        return render_template('news/index.html', data={"user_info":user.to_dict()})
    else:
        return render_template('news/index.html', data={"user_info":None})


@index_blueprint.route('/index.html')
def HomeIndexPage():
    return redirect(url_for('index.HomeTestPage'))


@index_blueprint.route('/favicon.ico')
def Sendfavicon():
    return current_app.send_static_file("news/favicon.ico")