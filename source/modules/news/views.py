from source.utility.response_code import RET
from . import news_blueprint
from flask import render_template, current_app, jsonify
from source.models import *



@news_blueprint.route('/<int:news_id>')
def Function_Loadnews(news_id):
    current_app.logger.debug(news_id)
    news=None
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
                "news":news.to_dict(),

            }
            return render_template('news/detail.html', data=data)
