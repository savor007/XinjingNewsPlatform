from flask import redirect

from . import user_blueprint
from flask import render_template, session, jsonify, request, g
from source.models import *
from source.utility.common import *
from source.utility.response_code import *
from source.utility.QiniuFileStorage import *





@user_blueprint.route('/news_release' , methods=['GET','POST'])
@Load_User_Info
def function_newsrelease():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="no user log in yet.")
    if request.method=='GET':
        try:
            Category_Items=list()
            category_dict_list =list()
            Category_Items=Category.query.all()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="database error for new category.")
        Catergory_List=list()
        for category_item in Category_Items:
            Catergory_List.append(category_item.to_dict())
        category_dict_list= Catergory_List[1:]
        data={
            "user_info": user.to_dict(),
            "categories": category_dict_list
        }
        return render_template('news/user_news_release.html', data=data)
    else:
        request_dict=request.json
        return jsonify(errno=RET.OK, errmsg="upload success.")




@user_blueprint.route('/news_list' , methods=['GET'])
@Load_User_Info
def function_newslist():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="no user log in yet.")
    page_index=request.args.get('page', 1)
    try:
        page=int(page_index)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg='Database error')
    current_page=1
    total_page=1
    released_newslist=list()
    try:
        news_object_list=News.query.filter(News.user_id== user.id).all().paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="error in searching database.")

    current_page = news_object_list.page
    total_page = news_object_list.pages
    news_items=news_object_list.items
    news_list=list()

    data={
        "user_info":user.to_dict,
        "news_list":[news_item.to_dict() for news_item in news_items]
    }
    return render_template('news/user_news_release.html', data=data)



@user_blueprint.route('/collection_info', methods=['GET'])
@Load_User_Info
def function_loadcollectednews():
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="no user log in yet.")
    page_data=request.args.get('page', 1)
    try:
        page_index=int(page_data)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="parameter error in int")
    Paginate_Data=None
    total_pages = 1
    current_page =1
    Colleceted_NewsList = list()
    try:
        Paginate_Data=user.collection_news.paginate(page_index, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg=' news collected error in database.')
    else:
        total_pages=Paginate_Data.pages
        current_page=Paginate_Data.page
        Colleceted_NewsList=Paginate_Data.items

        data={
            "total_pages":total_pages,
            "current_page":current_page,
            "collected_news_list": [news_item.to_dict() for news_item in Colleceted_NewsList]
        }
        return render_template('news/user_collection.html', data=data)


@user_blueprint.route('/password_update', methods=['POST', 'GET'])
@Load_User_Info
def Function_ChangePassword():
    user= g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="User has not log in yet.")
    if request.method == 'GET':
        data={
            "user_info": user.to_dict()
        }
        return render_template('news/user_pass_info.html', data=data)
    if request.method== 'POST':
        old_password=request.json.get('old_password')
        new_password=request.json.get('new_password')
        if not all([old_password, new_password]):
            return jsonify(errno=RET.PARAMERR, errmsg="No invalid Parameter sent.")
        if not user.check_passoword(old_password):
            return jsonify(errno=RET.PWDERR, errmsg="The old input password error")
        else:
            user.password=new_password
            try:
                NewsDB.session.commit()
            except Exception as error:
                current_app.logger.error(error)
                NewsDB.session.rollback()
                return jsonify(errno=RET.DBERR, errmsg="dababase error.")
            else:
                return jsonify(errno=RET.OK, errmsg="success")


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
            image_data= request.files.get("avatar").read()
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


