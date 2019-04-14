from flask import redirect

from . import user_blueprint
from flask import render_template, session, jsonify, request, g
from source.models import *
from source.utility.common import *
from source.utility.response_code import *
from source.utility.QiniuFileStorage import *


@user_blueprint.route('/pic_info', methods=['GET', 'POST'])
@Load_User_Info
def Function_UploadUserAvartar():
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=" User has not log in yet..")
    if request.method=='GET':
        data={
            "user_info":user.to_dict()
        }
        return render_template('news/user_pic_info.html', data=data)
    else:
        try:
            image_data=request.files.get().read
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DATAERR, errmsg="Image file reading error")
        image_key=StorageFile2RemoteServer(image_data)
        user.avatar_url=image_key
        try:
            NewsDB.session.commit()
        except Exception as error:
            NewsDB.session.rollback()
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="database error when saving image url to database.")
        return jsonify(errno=RET.OK, errmsg="Success", data={"avatar_url":constants.QINIU_DOMAIN_PREFIX+image_key})


@user_blueprint.route('/info', methods=['GET'])
@Load_User_Info
def Function_UserInfo():
    user=g.user
    if not user:
        return redirect('/')

    data={
        "user_info":user.to_dict()
    }

    return render_template("news/user.html", data=data)


@user_blueprint.route('/base_info' , methods=['GET', 'POST'])
@Load_User_Info
def Function_BaseUserInfor():
    user=g.user
    if request.method=='GET':
        data={
            "user_info":user.to_dict()
        }
        return render_template("news/user_base_info.html", data=data)
    if request.method=='POST':
        parameter=request.json
        signature_str=parameter.get('signature')
        nick_name_str=parameter.get('nick_name')
        gender = parameter.get('gender')
        if not all([signature_str,gender, nick_name_str]):
            return jsonify(errno=RET.PARAMERR, errmsg="In valid parameters")
        if gender not in ("MAN","WOMAN"):
            return jsonify(errno=RET.PARAMERR, errmsg="In valid parameters")
        user.gender=gender
        user.nick_name=nick_name_str
        user.signature=signature_str
        try:
            NewsDB.session.commit()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="error of data update")
        else:
            data={

                "user_info": user.to_dict()
            }
            return jsonify(errno=RET.OK, errmsg="update success" ,data=data)


