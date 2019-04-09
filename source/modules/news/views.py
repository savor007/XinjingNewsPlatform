from . import news_blueprint
from flask import render_template, current_app


@news_blueprint.route('/<int:news_id>')
def Function_Loadnews(news_id):
    current_app.logger.debug(news_id)
    return render_template('news/detail.html')
