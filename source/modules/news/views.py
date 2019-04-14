from source.utility.response_code import RET
from . import news_blueprint
from flask import g,render_template, current_app, jsonify, request
from source.models import *
from source.utility.common import *


@news_blueprint.route('/comment_like', methods= ["POST"])
@Load_User_Info
def Function_Comment_Like():
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="no user login yet")
    parameter=request.json

    try:
        comment_id_str = parameter.get('comment_id')
        news_id_str = parameter.get('news_id')
        action=parameter.get('action')
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="no data from post request.")
    if not all([comment_id_str,news_id_str,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="no enough data from post request.")
    try:
        current_app.logger.debug("comment text=%s, news_id=%s, action=%s" % (comment_id_str, news_id_str, action))
        news_id=int(news_id_str)
        comment_id=int(comment_id_str)
    except Exception as error:
        return jsonify(errno=RET.PARAMERR, errmsg="wrong data format from post request.")

    news=None
    news=News.query.get(news_id)
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="no news information in newslist")

    comment = None
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="no comment information in comment list.")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR,errmsg="the action is not allowed or not supported.")

    if action=="add":
        comment_like_object = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                       CommentLike.comment_id == comment_id).first()

        if not comment_like_object:
            comment_like_object = CommentLike()
            comment_like_object.comment_id = comment_id
            comment_like_object.user_id = user.id
            NewsDB.session.add(comment_like_object)
            comment.like_count+=1

    else:
        comment_like=CommentLike.query.filter(CommentLike.user_id==user.id, CommentLike.comment_id==comment_id).first()
        if comment_like:
            NewsDB.session.delete(comment_like)
            if comment.like_count > 0:
                comment.like_count-=1
    try:
        NewsDB.session.commit()
    except Exception as error:
        current_app.logger.error(error)
        NewsDB.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="database operation error")
    return jsonify(errno=RET.OK, errmsg="success")



@news_blueprint.route('/news_comment', methods=["POST"])
@Load_User_Info
def Function_Comments():
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="no user has not log in yet.")
    parameter = request.json
    try:
        comment_text = parameter['comment']
        news_id_str = parameter['news_id']
        parent_id_str=parameter.get('parent_id')
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR, errmsg="no data from post request.")
    if not all([comment_text,news_id_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="no enough data from post request.")
    try:
        current_app.logger.debug("comment text=%s, news_id=%s" % (comment_text, news_id_str))
        news_id=int(news_id_str)
    except Exception as error:
        return jsonify(errno=RET.PARAMERR, errmsg="wrong data format from post request.")

    news=None
    news=News.query.get(news_id)
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="no news information in newslist")

    if parent_id_str:
        try:
            parent_id=int(parent_id_str)
        except Exception as error:
            return jsonify(errno=RET.PARAMERR, errmsg="data format error from post request.")
        else:
            current_app.logger.debug("parend id="+parent_id_str)
    new_comment=Comment()
    new_comment.news_id=news_id
    if parent_id_str:
        new_comment.parent_id=parent_id
    new_comment.content=comment_text
    new_comment.user_id=user.id
    try:
        NewsDB.session.add(new_comment)
        NewsDB.session.commit()
    except Exception as error:
        current_app.logger.error(error)

    resp_data=new_comment.to_dict()

    return jsonify(errno=RET.OK, errmsg="comment succcess", data=resp_data)



@news_blueprint.route('/news_collect', methods=["POST"])
@Load_User_Info
def Function_Collection():
    parameter=request.json
    try:
        action=parameter['action']
        news_id_str=parameter['news_id']
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR,errmsg="no data from post request")
    if not all([action, news_id_str]):
        return jsonify(errno=RET.PARAMERR, errmsg= "No enough data from request.")
    current_app.logger.debug("news_id=%s, action=%s" % (news_id_str, action))
    try:
        news_id=int(news_id_str)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.PARAMERR,errmsg="Wrong data type of news id.")
    user=g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="User has not log in yet.")
    news=None
    news=News.query.get(news_id)
    if not news:
        return  jsonify(errno=RET.NODATA, errmsg="can not find the news by the news id.")
    if action=='collect':
        user.collection_news.append(news)
        return jsonify(errno=RET.OK,errmsg="collection success")
    elif action=='cancel_collect':
        if news in user.collection_news.all():
            user.collection_news.remove(news)
        return  jsonify(errno=RET.OK,errmsg="cancel collection success")
    else:
        return jsonify(errno=RET.PARAMERR, errmsg="unknown action.")






@news_blueprint.route('/<int:news_id>')
@Load_User_Info
def Function_Loadnews(news_id):
    current_app.logger.debug(news_id)
    news=None
    """get the user info by g, which is g.user is defined by decorator"""
    user=g.user
    """"""
    """get news ranking list"""
    try:
        NewsList=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg="error when searching news in database")
    if NewsList:
        news_elements=list()
        for news in NewsList:
            news_elements.append(news.to_basic_dict())
    """"""
    try:
        news=News.query.filter(News.id==news_id).first()
    except Exception as error:
        current_app.logger.error(error)
        return jsonify(errno=RET.DBERR, errmsg= "database accessing error")
    else:
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="can not find the news by id")
        else:
            news.clicks+=1
            news_collected = False
            if user:
                if news in user.collection_news.all():
                    news_collected=True
            """
            load all of the comments here
            """
            comment_list=list()
            comments_object_list=list()
            comment_id_liked=list()
            comments_object_list=Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc())
            if g.user:
                comment_like_object_bythisuser = CommentLike.query.filter(CommentLike.user_id == g.user.id).all()
                comment_id_liked=[comment_liked_t.comment_id for comment_liked_t in comment_like_object_bythisuser]
            for comment_object in comments_object_list:
                comment_dict=comment_object.to_dict()
                comment_dict["liked"]= False
                if comment_object.id in comment_id_liked:
                    comment_dict["liked"] = True
                # if g.user:
                #     comment_like_object= None
                #     comment_like_object=CommentLike.query.filter(CommentLike.comment_id==comment_object.id, CommentLike.user_id==g.user.id).first()
                #     if  comment_like_object:
                #         comment_dict["liked"] = True
                comment_list.append(comment_dict)

            """"""
            data={
                "user_info":user.to_dict() if user else None,
                "rankednews":news_elements,
                "news":news.to_dict(),
                "news_collected":news_collected,
                "news_comments":comment_list
            }

            return render_template('news/detail.html', data=data)
