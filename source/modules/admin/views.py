from flask import current_app, jsonify
from flask import render_template, request, session, redirect,g
from flask import url_for

from source.models import *
from source.utility.common import Load_User_Info
import datetime, time

from source.utility.response_code import RET
from . import admin_blueprint



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
