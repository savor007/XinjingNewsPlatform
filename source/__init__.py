import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
"""
#  use to set the storing position of session, go to the Session declaration and check its configuration
"""
from flask_session import Session
from Config import *

NewsDB=SQLAlchemy(app=None)



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
    redis_store=StrictRedis(host=RunningConfig[Configuration_Name].REDIS_HOST, port=RunningConfig[Configuration_Name].REDIS_PORT )
    return apps,logger

