from flask import Flask, session, make_response
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
"""
#  use to set the storing position of session, go to the Session declaration and check its configuration
"""
from flask_session import Session

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


class AppsConfiguration():
    DEBUG=True
    SECRET_KEY="yihy6b19b80ks79bMGiLw5P1B5Xo3wZkokOO537NaDUAH5hRVwYdJ8+k4F3XVhG0"
    SQLALCHEMY_DATABASE_URI='mysql://root:mysql@localhost:3306/NewsPlatformDatabase'
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    REDIS_HOST='Localhost'
    REDIS_PORT=6379
    SESSION_TYPE='redis'
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_KEY_PREFIX="session:"
    SESSION_USE_SIGNER=True
    SESSION_PERMANENT=False    # set to True means never expire
    PERMANENT_SESSION_LIFETIME=3600*72




apps = Flask(__name__)
apps.config.from_object(AppsConfiguration)
Session(apps)

NewsDB=SQLAlchemy(apps)
redis_store=StrictRedis(host=AppsConfiguration.REDIS_HOST, port=AppsConfiguration.REDIS_PORT )

AppManager = Manager(apps)
Migrate(apps, NewsDB)
AppManager.add_command('db',MigrateCommand)


@apps.route('/')
def HomeTestPage():
    session['username']="savor"
    session['password']="test"
    return make_response("Welcome to Home Test Page!")


if __name__ == '__main__':
    AppManager.run()


