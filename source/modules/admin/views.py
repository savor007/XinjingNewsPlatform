from flask import render_template, request, session, redirect
from source.models import *

from . import admin_blueprint


@admin_blueprint.route('/login', methods=['GET','POST'])
def Function_AdminLogin():
    error_str=""
    user = None
    if request.method=="GET":
        user_id=session.get('user_id',None)
        is_admin=session.get('is_admin', False)
        if user_id and is_admin:
            return redirect('/index')
        return render_template("admin/login.html", errmsg=error_str)
    else:
        username=request.form.get('username', None)
        password=request.form.get('password', None)
        if not all([username, password]):
            error_str="parameter are not enough for log in"
            return render_template("admin/login.html", errmsg=error_str)


        user=User.query.filter(User.mobile==username, User.password==password, User.is_admin==True).filter()
        if not user:
            return render_template("admin/login.html", errmsg="password error or admin not exist.")
        else:
            session['user_id'] = user.id
            session['user_mobile'] = user.mobile
            session['user_nickname'] = user.nick_name
            session['is_admin'] = user.is_admin
            return redirect("/index")



@admin_blueprint.route("/index", methods=['GET', 'POST'])
def Function_AdminIndex():
    if request.method=='GET':
        return render_template("admin/index.html")
