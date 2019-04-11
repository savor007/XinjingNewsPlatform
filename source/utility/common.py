#  this module is used to define common tools and functions, for both html template and server"
import functools
from flask import current_app,g, session
from source.models import User


def index_ranking_num_class(index):
    """ this function is used to return ranking num class with news index"""
    if index==0:
        return "first"
    elif index==1:
        return  "second"
    elif index==2:
        return "third"
    else:
        return ""


def Load_User_Info(func):
    @functools.wraps(func)
    def wrapper(*kargs, **kwargs):
        user=None
        user_id=session.get('user_id')
        if user_id:
            try:
                user=User.query.get(user_id)
            except Exception as error:
                current_app.logger.error(error)

        g.user=user
        return func(*kargs,**kwargs)
    return wrapper
