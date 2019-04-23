from flask import current_app, jsonify
from flask import render_template, request, session, redirect,g
from flask import url_for

from source.models import *
from source.utility.QiniuFileStorage import StorageFile2RemoteServer
from source.utility.common import Load_User_Info
import datetime, time

from source.utility.response_code import RET
from . import admin_blueprint



@admin_blueprint.route('/news_type_change', methods=['POST'])
def function_change_newscategory():
    category_id=request.json.get('category_id', None)
    new_category_name=request.json.get('category_name', None)
    action=request.json.get('action', None)
    if action.lower() not in ['add', 'change']:
        return jsonify(errno=RET.PARAMERR, errmsg="ACTION is not supported.")
    if not all([new_category_name]):
        return jsonify(errno=RET.PARAMERR, errmsg="parameter is not enough.")
    if category_id:
        try:
            category_id_num=int(category_id)
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.PARAMERR, errmsg="category id is in wrong format.")
    if action.lower()=='change':
        category_item=Category.query.get(category_id_num)
        if not category_item:
            return jsonify(errno=RET.NODATA, errmsg="database error")
        else:
            category_item.name=new_category_name
    if action.lower()== 'add':
        category_item=Category()
        category_item.name=new_category_name
        NewsDB.session.add(category_item)
    try:
        NewsDB.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        NewsDB.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="databased insertion error")
    else:
        return jsonify(errno=RET.OK, errmsg="success")


@admin_blueprint.route('/news_type', methods=['GET'])
def function_news_type():
    try:
        category_object_list= Category.query.all()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="retrieving error")
    category_list=list()
    for category_item in category_object_list:
        category_list.append(category_item.to_dict())
    data={
        "categories": category_list[1:]
    }
    return render_template('admin/news_type.html', data=data)



@admin_blueprint.route('/news_edit_action', methods=['POST'])
def function_edit_action():
    news_id_str=request.form.get('news_id', None)
    news_title=request.form.get('news_title',None)
    news_digest = request.form.get('news_digest', None)
    news_image = request.files.get('news_url', None)
    news_content=request.form.get('content', None)
    news_category_str=request.form.get('category_id', None)
    if not all([news_id_str, news_title, news_digest, news_content, news_category_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="Parameters are not enough.")
    try:
        news_id=int(news_id_str)
        news_category=int(news_category_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="parameter format error")
    news=News.query.get(news_id)
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="No data exist!!")
    news.content=news_content
    news.title= news_title
    news.digest= news_digest
    news.category_id=news_category
    if news_image:
        try:
            news_image_data=news_image.read()
            url=StorageFile2RemoteServer(news_image_data)
        except Exception as error:
            current_app.logger.error(error)
        else:
            news.index_image_url=constants.QINIU_DOMAIN_PREFIX+url

    try:
        NewsDB.session.commit()
    except Exception as error:
        NewsDB.session.rollback()
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="Database error")
    else:
        return jsonify(errno=RET.OK, errmsg="success")




@admin_blueprint.route('/news_edit_action', methods=['GET'])
def function_news_editaction():
    news_id_str=request.args.get('news_id',None)
    if not news_id_str:
        return jsonify(errno=RET.PARAMERR, errmsg="parameter error")
    try:
        news_id=int(news_id_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="news id format error")
    news=None
    categories=list()
    try:
        news=News.query.get(news_id)
        categories=Category.query.all()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="database error when query")
    if not news or categories==[]:
        return jsonify(errno=RET.NODATA, errmsg="no data return in query.")
    else:
        categories_list=list()
        category_select=list()
        categories.pop(0)
        for category_item in categories:
            category_dict=category_item.to_dict()
            if category_item.id==news.category_id:
                category_dict["is_selected"]=True
            else:
                category_dict["is_selected"]=False
            categories_list.append(category_dict)

        data={
            "news_info": news.to_dict(),
            "categories":categories_list
        }
        return render_template("admin/news_edit_detail.html", data=data)




@admin_blueprint.route('/news_edit', methods=['GET'])
def function_news_edition():
    news_list=list()
    errmsg=''
    page_str=request.args.get("page", "1")
    key_word=request.args.get("key_word", None)
    try:
        page=int(page_str)
    except Exception as error:
        current_app.logger.error(error)
        return render_template("admin/news_edit.html", data={"news_list": news_list}, errmsg="page formagt error.")

    try:
        if not key_word:
            News_List_Object=News.query.filter(News.status==0).order_by(News.create_time.desc()). \
                paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        else:
            News_List_Object = News.query.filter(News.status == 0, News.title.contains(key_word)).order_by(News.create_time.desc()). \
                paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

    except Exception as error:
        current_app.logger.error(error)
        return render_template("admin/news_edit.html", data={"news_list": news_list}, errmsg=errmsg)
    total_page=News_List_Object.pages
    current_page=News_List_Object.page
    news_list=[news_item.to_dict() for news_item in News_List_Object.items]
    data={
        "news_list":news_list,
        "current_page":current_page,
        "total_page":total_page,
        "keyword":key_word
    }
    return render_template("admin/news_edit.html", data=data, errmsg=errmsg)




@admin_blueprint.route('/news_review_action', methods=['POST'])
def Function_NewsReviewAction():
    action=request.json.get('action', None)
    reason=request.json.get('reason', None)
    news_id_str=request.json.get('news_id', None)
    if not all([action, news_id_str]):
        return jsonify(errno=RET.PARAMERR, errmsg='parameters are not enough.')
    if action.lower() not in ['approve', 'reject']:
        return jsonify(errno=RET.PARAMERR, errmsg="parameter error")

    try:
        news_id= int(news_id_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="News ID format error")
    news=News.query.filter(News.id==news_id, News.status!=0).first()
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="News doesn't exist!")
    if action.lower()=='approve':
        news.status=0
    else:
        reason=request.json.get('reason', None)
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="The reason of rejection can not be empty.")
        else:
            news.status=-1
            news.reason=reason
    try:
        NewsDB.session.commit()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="database update error.")
    else:
        return jsonify(errno=RET.OK, errmsg="Action Complete.")




@admin_blueprint.route('/news_review_detail')
def Function_NewsReviewDetail():
    news_id_str=request.args.get('news_id',"1")
    try:
        news_id=int(news_id_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="parameter format error for page")

    news_review = None
    try:
        news_review = News.query.filter(News.id == news_id).first()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="database error")
    if not news_review:
        return jsonify(errno=RET.NODATA, errmsg="can not find the news by the id")
    news_info = news_review.to_dict()
    # print(news_id_str)
    return render_template('admin/news_review_detail.html', data={"news_info": news_info})



@admin_blueprint.route('/news_review')
def Function_NewsReview():
    Newslist=list()
    total_page=1
    current_page=1
    page_str=request.args.get('page', "1")
    key_word=request.args.get('keyword',"")
    try:
        page=int(page_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="parameter format error for page")
    try:
        if key_word == "":
            News_Pages_list=News.query.filter(News.status!=0).order_by(News.create_time.desc()). \
                paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        else:
            News_Pages_list = News.query.filter(News.status != 0, News.title.contains(key_word)).order_by(News.create_time.desc()). \
                paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="Database error")
    total_page=News_Pages_list.pages
    current_page=News_Pages_list.page
    News_Items=News_Pages_list.items
    for news in News_Items:
        Newslist.append(news.to_review_dict())
    context={
        "total_page":total_page,
        "current_page":current_page,
        "News_Review_List":Newslist
    }
    return render_template('admin/news_review.html', data=context)




@admin_blueprint.route('/user_list')
@Load_User_Info
def Function_Userlist():
    user_list=list()
    total_page = 1
    current_page = 1
    page_str=request.args.get('page', 1)
    try:
        page=int(page_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="parameter format error for page")
    try:
        User_Pages=User.query.filter(User.is_admin==False).order_by(User.create_time.desc()).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="Database error")
    User_Objects=User_Pages.items
    total_page=User_Pages.pages
    current_page=User_Pages.page
    for user_object in User_Objects:
        user_list.append(user_object.to_admin_dict())
    data={
        "user_list":user_list,
        "total_page":total_page,
        "current_page":current_page

    }
    return render_template("admin/user_list.html", data=data)

@admin_blueprint.route('/user_count')
@Load_User_Info
def Function_UserCount():
    total_count=0
    add_count_thismonth=0
    add_count_today=0
    active_date=list()
    active_count=list()
    current_time= time.localtime()
    # time.struct_time(tm_year=2019, tm_mon=4, tm_mday=19, tm_hour=22, tm_min=36, tm_sec=12, tm_wday=4, tm_yday=109, tm_isdst=0)
    month_begin_time_str="%04d-%02d-1" % (current_time.tm_year, current_time.tm_mon)
    month_begin_time=datetime.datetime.strptime(month_begin_time_str, "%Y-%m-%d")

    today_begin_time_str = "%04d-%02d-%02d" % (current_time.tm_year, current_time.tm_mon, current_time.tm_mday)
    today_begin_time = datetime.datetime.strptime(today_begin_time_str,"%Y-%m-%d")
    try:
        total_count=User.query.filter(User.is_admin==False).count()
        add_count_thismonth = User.query.filter(User.is_admin == False, User.create_time>=month_begin_time).count()
        add_count_today = User.query.filter(User.is_admin == False, User.create_time>=today_begin_time).count()
    except Exception as error:
        current_app.logger.error(error)

    index=0
    for index in range(0,31):
        start_query_date=today_begin_time-datetime.timedelta(days=index)
        end_query_date=start_query_date+datetime.timedelta(days=1)
        active_date_element=start_query_date.strftime("%Y-%m-%d")
        try:
            active_count_element=User.query.filter(User.is_admin==False, User.last_login>=start_query_date, User.last_login<=end_query_date).count()
        except Exception as error:
            current_app.logger.error(error)
            print("query stop in the iteration of "+ str(index))
            break
        active_count.append(active_count_element)
        active_date.append(active_date_element)

    active_count.reverse()
    active_date.reverse()
    data={
        "total_usercount":total_count,
        "usecount_this_month":add_count_thismonth,
        "usecount_today":add_count_today,
        "active_date_array":active_date,
        "active_count_array": active_count
    }
    return render_template("admin/user_count.html", data=data)


@admin_blueprint.route('/login', methods=['GET','POST'])
def Function_AdminLogin():
    error_str=""
    user = None
    if request.method=="GET":
        user_id=session.get('user_id',None)
        is_admin=session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.Function_AdminIndex'))
        return render_template("admin/login.html", errmsg=error_str)
    else:
        username=request.form.get('username', None)
        password=request.form.get('password', None)
        if not all([username, password]):
            error_str="parameter are not enough for log in"
            return render_template("admin/login.html", errmsg=error_str)


        user=User.query.filter(User.mobile==username, User.is_admin==True).first()
        if not user:
            return render_template("admin/login.html", errmsg="password error or admin not exist.")
        elif user.check_passoword(password):
            session['user_id'] = user.id
            session['user_mobile'] = user.mobile
            session['user_nickname'] = user.nick_name
            session['is_admin'] = user.is_admin
            return redirect(url_for('admin.Function_AdminIndex'))
        else:
            return render_template("admin/login.html", errmsg="wrong password")



@admin_blueprint.route("/index", methods=['GET', 'POST'])
@Load_User_Info
def Function_AdminIndex():
    if request.method=='GET':
        user=None
        user=g.user
        return render_template("admin/index.html", data={"user_info":user.to_dict()})
