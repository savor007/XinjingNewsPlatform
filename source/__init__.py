import logging

from flask import Flask, render_template
import flask_wtf.csrf as CSRF_Module

from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()     #  this is the solution for the error of database migration::ImportError: No module named 'MySQLdb'
"""
Migration use the MYSQLDB as default database library. In Python3, it is called pymysql
"""

"""
#  use to set the storing position of session, go to the Session declaration and check its configuration
"""
from flask_session import Session
from Config import *

NewsDB=SQLAlchemy(app=None)
redis_store=None



def setup_log(config_name):
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)
    log_file_handler=logging.FileHandler("./logs/log.txt", mode='a')
    log_file_handler.setLevel(RunningConfig[config_name].LOG_LEVEL)

    logformat=logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d]-%(levelname)s: %(message)s")

    log_file_handler.setFormatter(logformat)
    logger.addHandler(log_file_handler)
    return logger



def CreateRunningApps(Configuration_Name):
    logger=setup_log(Configuration_Name)
    apps = Flask(__name__)
    apps.config.from_object(RunningConfig[Configuration_Name])
    NewsDB.init_app(apps)
    Session(apps)
    from flask_wtf.csrf import CsrfProtect
    CSRF_Module.CSRFProtect(apps)
    global redis_store
    redis_store=StrictRedis(host=RunningConfig[Configuration_Name].REDIS_HOST, port=RunningConfig[Configuration_Name].REDIS_PORT,decode_responses=True)
    """
    for redis_store: set decode_response= True, otherwise, the get result is in byte
    """

    """
    add customized the filer to html
    """
    from source.utility.common import index_ranking_num_class
    apps.add_template_filter(index_ranking_num_class, "index_ranking_num_class")    # import common to load filter function
    """
    register error handler
    """
    @apps.errorhandler(404)
    def SendErrorPage(error):
        logger.error(error)

        return render_template('news/404.html')

    @apps.after_request
    def SetCookiesforRequest(response):
        csrfcode=CSRF_Module.generate_csrf()
        # print(csrfcode)
        response.set_cookie("csrf_token",csrfcode)
        logger.debug("csrf_token given by server" + csrfcode)
        return response

    from source.modules.index import index_blueprint
    apps.register_blueprint(index_blueprint)
    from source.modules.passport import passport_blueprint
    apps.register_blueprint(passport_blueprint)
    from source.modules.news import news_blueprint
    apps.register_blueprint(news_blueprint)
    from source.modules.users import user_blueprint
    apps.register_blueprint(user_blueprint)
    return apps,logger

