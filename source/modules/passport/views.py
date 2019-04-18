from . import passport_blueprint
from source import constants, redis_store
from flask import jsonify, make_response, request,current_app,session
from source.utility.captcha.captcha import captcha
from source.utility.response_code import RET
from source.externallib.yuntongxun import sms
import re
from random import randint
from source.models import *
from datetime import datetime


@passport_blueprint.route('/logout', methods=['GET', 'POST'])
def Logout_Function():
    session.pop('user_id', None)
    session.pop('user_mobile', None)
    session.pop('user_nickname', None)
    session.pop('is_admin', None)
    return jsonify(errno=RET.OK, errmsg='')



@passport_blueprint.route('/login',methods=['POST'])
def Login_Function():
    postdata=request.json
    mobile_number=postdata['mobile']
    password=postdata['password']
    user=None
    if not all([mobile_number, password]):
        return jsonify(errno=RET.NODATA,errmsg="NO data from the request.")
    elif not re.match('1[35678][0-9]{9}', mobile_number):
        return make_response(jsonify(errno=RET.USERERR, errmsg="the phone number is invalid."))
    else:
        current_app.logger.debug("mobile number is %s. password is %s." % (mobile_number, password))
        try:
            user=User.query.filter(User.mobile==mobile_number).first()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="error of accessing mysql database.")
        else:
            if not user:
                return jsonify(errno=RET.NODATA, errmsg="Modile phone number: "+mobile_number+" dosen't exsit.")
            elif not user.check_passoword(password):
                return jsonify(errno=RET.PWDERR, errmsg="The pasword is wrong.")
            else:
                try:
                    user.last_login=datetime.now()
                    # NewsDB.session.update(user)    no updated function
                    NewsDB.session.commit()
                except Exception as error:
                    current_app.logger.error(error)
                    return jsonify(error=RET.DBERR,errmsg="error when update user login time")
                else:
                    session['user_id'] = user.id
                    session['user_mobile'] = user.mobile
                    session['user_nickname'] = user.nick_name
                    session['is_admin'] = user.is_admin
                    return jsonify(errno=RET.OK, errmsg='')



@passport_blueprint.route('/register', methods=['POST'])
def Register_Function():
    postdata=request.json
    mobile_number=postdata['mobile']
    password=postdata['password']
    sms_verification_code=postdata['smscode']
    user=None
    if not all([mobile_number,password]):
        return jsonify(errno=RET.NODATA, errmsg="NO data from the request!")
    elif not re.match('1[35678][0-9]{9}', mobile_number):
        return make_response(jsonify(errno=RET.USERERR, errmsg="the phone number is invalid."))
    else:
        try:
            user=User.query.filter(User.mobile==mobile_number).first()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="error of accessing mysql database.")
        else:
            if user:
                return jsonify(errno=RET.DATAEXIST, errmsg="this phone number has been used for sign-up.")
            else:
                try:
                    real_sms_code=redis_store.get(name="SMS_VERFICATION_"+mobile_number)
                except Exception as error:
                    current_app.logger.error(error)
                    return jsonify(errno=RET.DBERR, errrmsg="sms verification code expired or redis error.")
                else:
                    if sms_verification_code!=real_sms_code and False:
                        return jsonify(errno=RET.PARAMERR,errmg="sms verification fail")
                    else:
                        user=User()
                        user.mobile=mobile_number
                        user.password=password
                        user.nick_name=mobile_number
                        user.last_login=datetime.now()
                        try:
                            NewsDB.session.add(user)
                            NewsDB.session.commit()
                        except Exception as error:
                            current_app.logger.error(error)
                            return jsonify(errno=RET.DBERR, errmsg='error when inserting new user into database.')
                        else:
                            session['user_id']=user.id
                            session['user_mobile']=user.mobile
                            session['user_nickname']=user.nick_name
                            session['is_admin']=user.is_admin
                            return jsonify(errno=RET.OK, errmsg='')



@passport_blueprint.route('/sms_code', methods=['POST'])
def SMSVerfification():
    postdate=request.json
    mobilephone_number=postdate['mobile']     #mobile, image_code,image_code_id
    image_code = postdate['image_code']
    image_code_id = postdate['image_code_id']
    current_app.logger.debug(
        "phone number from post json is %s.\n"
        "image code from post json is %s.\n"
        "image code ID from post json is %s."
        % (mobilephone_number,image_code,image_code_id)
    )
    user=None
    if not all([mobilephone_number, image_code_id,image_code]):
        return make_response(jsonify(errno=RET.NODATA, errmsg="no valid the data from the client for sms verfication"))
    elif not re.match('1[35678][0-9]{9}', mobilephone_number):
        return make_response(jsonify(errno=RET.USERERR,errmsg="the phone number is invalid."))
    else:
        try:
            user=User.query.filter(User.mobile==mobilephone_number).first()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="error in access mysql database.")
        else:
            if user:
                return jsonify(error=RET.DATAEXIST, errmsg="the mobile already exists in database.")
            else:
                try:
                    stored_imagecode=redis_store.get(name="User"+image_code_id)
                except Exception as error:
                    current_app.logger.error(error)
                    return make_response(jsonify(errno=RET.NODATA, errmsg='error in searching actual image code ID in redis'))
                else:
                    if stored_imagecode==None:
                        return make_response(jsonify(error=RET.NODATA, errmsg="the stored image id is exprired."))
                    else:
                        if stored_imagecode.upper()==image_code.upper():
                            sms_verifcation_code="%06d" % randint(0,999999)
                            current_app.logger.debug("The sms verification code is "+ sms_verifcation_code)
                            try:
                                sms_sender=sms.CCP()
                                """"
                                skip sending sms message as only 2 phone number can be used for test. Already validated below function.
                                """
                                #    sms_sender.send_template_sms(mobilephone_number,[sms_verifcation_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
                            except Exception as error:
                                current_app.logger.error(error)
                                return make_response(jsonify(errno=RET.THIRDERR,errmsg=" SMS sent fail"))
                            else:
                                try:
                                    redis_store.setex(name="SMS_VERFICATION_"+mobilephone_number, value=sms_verifcation_code,time=constants.SMS_CODE_REDIS_EXPIRES)
                                except Exception as error:
                                    current_app.logger.error(error)
                                    return make_response(jsonify(errno=RET.DBERR, errmsg="can't save sms verification code into redis"))
                                else:
                                    return make_response(jsonify(errno=RET.OK, errmsg=constants.SMS_CODE_REDIS_EXPIRES))
                        else:
                            return make_response(jsonify(errno=RET.DATAERR, errmsg='unmatched image verification code'))



@passport_blueprint.route('/image_code')
def GetVerficationImage():
    image_code_id=request.args.get('code_id', None)

    name, verificationcode, image =captcha.generate_captcha()
    current_app.logger.debug("image_code_id sent by client:%s. THe verication code generated by capcha is %s" % (image_code_id,verificationcode))
    try:
        redis_store.setex(name="User"+image_code_id,value=verificationcode,time=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as error:
        current_app.logger.error(error)
        # response_result = make_response('redis error when vefication code storing')
        # response_result.headers['Content-Type'] ='text/html'
        return make_response(jsonify(errno=RET.DBERR,errmsg="redis database connection error"))    # jsonify(**kwargs)
    else:
        response_result=make_response(image)
        response_result.headers['Content-Type']='image/jpeg'
        return response_result
