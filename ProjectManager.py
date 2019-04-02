from flask import session, make_response
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from Config import *
from source import NewsDB, CreateRunningApps

apps=CreateRunningApps(RunningConfig["Development"])
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
