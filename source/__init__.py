from flask import Flask
from flask_sqlalchemy import SQLAlchemy
"""
#  use to set the storing position of session, go to the Session declaration and check its configuration
"""
from flask_session import Session
from Config import *

NewsDB=SQLAlchemy(app=None)


def CreateRunningApps(Configuration_Name):
    apps = Flask(__name__)
    apps.config.from_object(RunningConfig[Configuration_Name])
    NewsDB.init_app(apps)
    Session(apps)
    redis_store=StrictRedis(host=RunningConfig[Configuration_Name].REDIS_HOST, port=RunningConfig[Configuration_Name].REDIS_PORT )
    return apps

