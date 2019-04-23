from source.utility.response_code import RET
from . import index_blueprint
from flask import g,url_for,session,request,make_response, render_template,redirect,current_app, jsonify
from source import redis_store, NewsDB  # try to use the redis_store here, not a must, depending the request logic
from source.models import *
from source.utility.common import *


@index_blueprint.route('/')
def HomeTestPage():
    user_id=session.get('user_id')
    # session['password']="test"
    # redis_store.set("test","onging")
    """
    load ranking news below:
    """
    category_list=list()
    try:
        categories=Category.query.all()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="error when searching news in database")
    if categories:
        category_list= [category.to_dict() for category in categories]

    NewsList=None
    try:
        NewsList=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="error when searching news in database")

    if NewsList:
        news_elements=list()
        for news in NewsList:
            news_elements.append(news.to_basic_dict())
    user=None
    if user_id:    #  user already log in
        try:
            user=User.query.filter(User.id==user_id).first()
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="database access erroor when search user avatar.")
    if user:
        return render_template('news/index.html', data={"user_info": user.to_dict(), "rankednews":news_elements,"categories":category_list})
    else:
        return render_template('news/index.html', data={"user_info": None, "rankednews": news_elements, "categories":category_list})


@index_blueprint.route('/index.html')
def HomeIndexPage():
    return redirect(url_for('index.HomeTestPage'))


@index_blueprint.route('/favicon.ico')
def Sendfavicon():
    return current_app.send_static_file("news/favicon.ico")



@index_blueprint.route('/loadcategory', methods=['GET'])
def LoadCatoryFuntion():
    try:
        Category_List=Category.query.all()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno= RET.DBERR, errmsg= "Database query error.")
    else:
        Category_Result=list()
        for category in Category_List:
            Category_Result.append(category.to_dict())
        return jsonify(errno=RET.OK, errmsg="OK", data=Category_Result)



@index_blueprint.route('/newslist')
def ViewFunction_LoadNewsList():
    category_id_raw=request.args.get('cid', "1")
    page_raw=request.args.get('page',"1")
    per_page_raw=request.args.get('per_page',constants.HOME_PAGE_MAX_NEWS)
    try:
        category_id=int(category_id_raw)
        page=int(page_raw)
        per_page=int(per_page_raw)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg= "the data format is wrong.")
    else:
        current_app.logger.debug("parameter from request. category_id=%d, page=%d, per_page_number=%d." % (category_id, page, per_page))

        try:
            if category_id!=1:
                NewsPages_Object= News.query.filter(News.category_id==category_id, News.status==0).order_by(News.create_time.desc()).paginate(page, per_page)
            else:
                NewsPages_Object = News.query.filter(News.status==0).order_by(News.create_time.desc()).paginate(page, per_page)     # order_by 前面不能加all(),加all()意味着list
        except Exception as error:
            current_app.logger.error(error)
            return jsonify(errno=RET.DBERR, errmsg="Database query issue")
        else:
            total_page=NewsPages_Object.pages
            current_page=NewsPages_Object.page
            NewsPage_List=[]
            for news_object in NewsPages_Object.items:
                NewsPage_List.append(news_object.to_dict())
            return jsonify(errno=RET.OK, errmsg= "OK", data=NewsPage_List, totalpage_num=total_page, current_page_num=current_page)







