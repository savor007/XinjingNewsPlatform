from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

from source import constants
from . import NewsDB


class BaseModel():
    """Base Class, create the setup time and update time for all of the models #"""
    create_time=NewsDB.Column(NewsDB.DateTime, default=datetime.now)   # create setup time
    update_time=NewsDB.Column(NewsDB.DateTime, default=datetime.now, onupdate=datetime.now)    # create update time



tb_user_collection=NewsDB.Table(
    "info_user_collection",
    NewsDB.Column("user_id",NewsDB.Integer,NewsDB.ForeignKey("info_user.id"), primary_key=True),
    NewsDB.Column("news_id", NewsDB.Integer, NewsDB.ForeignKey("info_news.id"), primary_key=True),
    NewsDB.Column("create_time", NewsDB.DateTime,default=datetime.now)
)


tb_user_follows=NewsDB.Table(
    "info_user_fans",
    NewsDB.Column('follower_id',NewsDB.Integer, NewsDB.ForeignKey('info_user.id'), primary_key=True),
    NewsDB.Column('Followed_id', NewsDB.Integer,NewsDB.ForeignKey('info_user.id'), primary_key=True)
)



class User(BaseModel, NewsDB.Model):
    """user table"""
    __tablename__="info_user"
    id=NewsDB.Column(NewsDB.Integer, primary_key=True)
    nick_name=NewsDB.Column(NewsDB.String(32),unique=True, nullable=False)
    password=NewsDB.Column(NewsDB.String(128), nullable=False)
    phone_number=NewsDB.Column(NewsDB.String(11),unique=True,nullable=False)
    last_login_time=NewsDB.Column(NewsDB.DateTime, default=datetime.now)
    avatar_url=NewsDB.Column(NewsDB.String(256))    # the path to save the phote of user
    is_admin=NewsDB.Column(NewsDB.Boolean, default=False)
    signature=NewsDB.Column(NewsDB.String(512))      # the signature of user
    gender=NewsDB.Column(
        NewsDB.Enum(
            "MAN", "WOMEN","UNKNOWN"
        ),
        default="UNKNOWN"
    )

    collection_news=NewsDB.relationship("News", secondary=tb_user_collection, lazy="dynamic")
    followers=NewsDB.relationship("User",
                                  secondary=tb_user_follows,
                                  primaryjoin=tb_user_follows.c.Followed_id,
                                  secondaryjoin=tb_user_follows.c.follower_id,
                                  backref=NewsDB.backref('followed', lazy='dynamic'),
                                  lazy="dynamic"
                                  )

    news_list=NewsDB.relationship("News", backref='user', lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("this attribute is not open for reading!")


    @password.setter
    def password(self, value):
        self.password_hash=generate_password_hash(value)


    def check_password(self, password):
        return check_password_hash(self.password_hash,password)


    def to_dict(self):
        resp_dict={
            "id":self.id,
            "nick_name":self.nick_name,
            "avatar_url":constants.QINIU_DOMAIN_PREFIX+self.avatar_url if self.avatar_url else "",
            "phone_number":self.phone_number,
            "gender":self.gender if self.gender else "UNKNOWN",
            "signature":self.signature if self.signature else "",
            "followers_count":self.followers.count(),
            "news_count":self.news_list.count()
        }
        return resp_dict

    def to_admin_dict(self):
        resp_dict={
            "id":self.id,
            "nick_name":self.nick_name,
            "phone_number":self.phone_number,
            "register_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login_time":self.last_login_time.strftime("%Y-%m-%d %H:%M:%S"),
        }


class News(BaseModel, NewsDB.Model):
    __tablename__="info_news"
    id=NewsDB.Column(NewsDB.Integer,primary_key=True)
    title=NewsDB.Column(NewsDB.String(256),nullable=False)
    source=NewsDB.Column(NewsDB.String(256),nullable=False)
    digest=NewsDB.Column(NewsDB.String(512), nullable=False)
    content=NewsDB.Column(NewsDB.Text, nullable=False)
    clicks=NewsDB.Column(NewsDB.Integer,default=0)
    index_image_url=NewsDB.Column(NewsDB.String(256))       # the path of the picture of the news list
    category_id=NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_category.id"))
    user_id=NewsDB.Column(NewsDB.Integer,NewsDB.ForeignKey("info_user.id"))
    status=NewsDB.Column(NewsDB.Integer,default=0)
    """
        # the current status of the news, 0: pass audit, 1: in the process of audit, -1: unqualified
        """

    reason=NewsDB.Column(NewsDB.String(256),default="")     # the reason of unqualified
    comments=NewsDB.relationship('Comment', lazy="dynamic")

    def to_review_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "reason": self.reason if self.reason else ""
        }
        return resp_dict

    def to_basic_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "index_image_url": self.index_image_url,
            "clicks": self.clicks,
        }
        return resp_dict

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "comments_count": self.comments.count(),
            "clicks": self.clicks,
            "category": self.category.to_dict(),
            "index_image_url": self.index_image_url,
            "author": self.user.to_dict() if self.user else None
        }
        return resp_dict


class Comment(BaseModel, NewsDB.Model):
    __tablename__="info_comment"
    id=NewsDB.Column(NewsDB.Integer, primary_key=True)
    user_id=NewsDB.Column(NewsDB.Integer,NewsDB.ForeignKey("info_user.id"), nullable=False)
    news_id=NewsDB.Column(NewsDB.Integer,NewsDB.ForeignKey("info_news.id"), nullable=False)
    content=NewsDB.Column(NewsDB.Text, nullable=False)
    comment_parent_id=NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_comment.id"))
    comment_parent=NewsDB.relationship("comment", remote_side=[id])
    like_count=NewsDB.Column(NewsDB.Integer,default=0)

    def to_dic(self):
        resp_dict={
            "id":self.id,
            "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content":self.content,
            "parent":self.comment_parent.to_dict() if self.comment_parent else None,
            "user": User.query.get(self.user_id).to_dict(),
            "news_id":self.news_id,
            "like_count":self.like_count

        }
        return resp_dict


class CommentLike(BaseModel, NewsDB.Model):
    """ endorsement for comments"""
    __tablename__="info_comment_endorsement"
    comment_id=NewsDB.Column("comment_id", NewsDB.Integer,NewsDB.ForeignKey("info_comment.id"), primary_key=True)
    user_id=NewsDB.Column("user_id", NewsDB.Integer,NewsDB.ForeignKey("info_user.id"), primary_key=True)


class Category(BaseModel,NewsDB.Model):
    """new category"""
    __tablename__="info_category"
    id=NewsDB.Column(NewsDB.Integer, primary_key=True)
    name=NewsDB.Column(NewsDB.String(128), nullable=False)
    news_list=NewsDB.relationship('News', backref="category", lazy='dynamic')


    def to_dict(self):
        resp_dict={
            "id":self.id,
            "name":self.name,
        }
        return resp_dict