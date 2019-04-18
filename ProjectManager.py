from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from source.models import *
from flask import session
import logging

from source import NewsDB, CreateRunningApps, models

apps, logger=CreateRunningApps("Development")
AppManager = Manager(apps)
Migrate(apps, NewsDB)
AppManager.add_command('db',MigrateCommand)


@AppManager.option('-u', '-username', dest="username")
@AppManager.option('-p', '-password', dest="password")
def create_admin_Command(username, password):
    user=None
    if not all([username, password]):
        print("parameters are not enough.")
    user=User.query.filter(User.mobile==username, User.password==password).first()
    if user:
        print("user already exist")
    user=User()
    user.is_admin=True
    user.password=password
    user.mobile=username
    user.nick_name=username
    # session['user_id'] = user.id
    # session['user_mobile'] = user.mobile
    # session['user_nickname'] = user.nick_name
    # session['is_admin'] = user.is_admin
    NewsDB.session.add(user)
    try:
        NewsDB.session.commit()
    except Exception as error:
        News.session.rollback()
        print("database insertion error")




if __name__ == '__main__':
    AppManager.run()
