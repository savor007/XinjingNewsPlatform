from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import logging

from source import NewsDB, CreateRunningApps, models

apps, logger=CreateRunningApps("Development")
AppManager = Manager(apps)
Migrate(apps, NewsDB)
AppManager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    AppManager.run()
