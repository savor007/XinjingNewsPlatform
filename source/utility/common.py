#  this module is used to define common tools and functions, for both html template and server"


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