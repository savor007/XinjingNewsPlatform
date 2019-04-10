from source.utility.response_code import RET
from . import news_blueprint
from flask import g,render_template, current_app, jsonify
from source.models import *
from source.utility.common import *


@news_blueprint.route('/<int:news_id>')
@Load_User_Info
def Function_Loadnews(news_id):
    current_app.logger.debug(news_id)
    news=None
    """get the user info by g, which is g.user is defined by decorator"""
    user=g.user
    """"""
    """get news ranking list"""
    try:
        NewsList=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="error when searching news in database")
    if NewsList:
        news_elements=list()
        for news in NewsList:
            news_elements.append(news.to_basic_dict())
    """"""
    try:
        news=News.query.filter(News.id==news_id).first()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg= "database accessing error")
    else:
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="can not find the news by id")
        else:
            news.clicks+=1
            data={
                "user_info":user.to_dict() if user else None,
                "rankednews":news_elements,
                "news":news.to_dict(),

            }
            return render_template('news/detail.html', data=data)
