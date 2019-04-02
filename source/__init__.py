from flask import Flask
from flask_sqlalchemy import SQLAlchemy
"""
#  use to set the storing position of session, go to the Session declaration and check its configuration
"""
from flask_session import Session
from redis import StrictRedis


NewsDB=SQLAlchemy(app=None)


def CreateRunningApps(Configuration):
    apps = Flask(__name__)
    apps.config.from_object(Configuration)
    NewsDB.init_app(apps)
    Session(apps)
    redis_store=StrictRedis(host=Configuration.REDIS_HOST, port=Configuration.REDIS_PORT )
    return apps

