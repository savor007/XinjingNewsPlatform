from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

from source import constants
from . import NewsDB


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = NewsDB.Column(NewsDB.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = NewsDB.Column(NewsDB.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


# 用户收藏表，建立用户与其收藏新闻多对多的关系
tb_user_collection = NewsDB.Table(
    "info_user_collection",
    NewsDB.Column("user_id", NewsDB.Integer, NewsDB.ForeignKey("info_user.id"), primary_key=True),  # 新闻编号
    NewsDB.Column("news_id", NewsDB.Integer, NewsDB.ForeignKey("info_news.id"), primary_key=True),  # 分类编号
    NewsDB.Column("create_time", NewsDB.DateTime, default=datetime.now)  # 收藏创建时间
)

tb_user_follows = NewsDB.Table(
    "info_user_fans",
    NewsDB.Column('follower_id', NewsDB.Integer, NewsDB.ForeignKey('info_user.id'), primary_key=True),  # 粉丝id
    NewsDB.Column('followed_id', NewsDB.Integer, NewsDB.ForeignKey('info_user.id'), primary_key=True)  # 被关注人的id
)


class User(BaseModel, NewsDB.Model):
    """用户"""
    __tablename__ = "info_user"

    id = NewsDB.Column(NewsDB.Integer, primary_key=True)  # 用户编号
    nick_name = NewsDB.Column(NewsDB.String(32), unique=True, nullable=False)  # 用户昵称
    password_hash = NewsDB.Column(NewsDB.String(128), nullable=False)  # 加密的密码
    mobile = NewsDB.Column(NewsDB.String(11), unique=True, nullable=False)  # 手机号
    avatar_url = NewsDB.Column(NewsDB.String(256))  # 用户头像路径
    last_login = NewsDB.Column(NewsDB.DateTime, default=datetime.now)  # 最后一次登录时间
    is_admin = NewsDB.Column(NewsDB.Boolean, default=False)
    signature = NewsDB.Column(NewsDB.String(512))  # 用户签名
    gender = NewsDB.Column(  # 订单的状态
        NewsDB.Enum(
            "MAN",  # 男
            "WOMAN"  # 女
        ),
        default="MAN")

    # 当前用户收藏的所有新闻
    collection_news = NewsDB.relationship("News", secondary=tb_user_collection, lazy="dynamic")  # 用户收藏的新闻
    # 用户所有的粉丝，添加了反向引用followed，代表用户都关注了哪些人
    followers = NewsDB.relationship('User',
                                secondary=tb_user_follows,
                                primaryjoin=id == tb_user_follows.c.followed_id,
                                secondaryjoin=id == tb_user_follows.c.follower_id,
                                backref=NewsDB.backref('followed', lazy='dynamic'),
                                lazy='dynamic')

    # 当前用户所发布的新闻
    news_list = NewsDB.relationship('News', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("当前属性不可读")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_passoword(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "avatar_url": constants.QINIU_DOMAIN_PREFIX + self.avatar_url if self.avatar_url else "",
            "mobile": self.mobile,
            "gender": self.gender if self.gender else "MAN",
            "signature": self.signature if self.signature else "",
            "followers_count": self.followers.count(),
            "news_count": self.news_list.count()
        }
        return resp_dict

    def to_admin_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "mobile": self.mobile,
            "register": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return resp_dict


class News(BaseModel, NewsDB.Model):
    """新闻"""
    __tablename__ = "info_news"

    id = NewsDB.Column(NewsDB.Integer, primary_key=True)  # 新闻编号
    title = NewsDB.Column(NewsDB.String(256), nullable=False)  # 新闻标题
    source = NewsDB.Column(NewsDB.String(64), nullable=False)  # 新闻来源
    digest = NewsDB.Column(NewsDB.String(512), nullable=False)  # 新闻摘要
    content = NewsDB.Column(NewsDB.Text, nullable=False)  # 新闻内容
    clicks = NewsDB.Column(NewsDB.Integer, default=0)  # 浏览量
    index_image_url = NewsDB.Column(NewsDB.String(256))  # 新闻列表图片路径
    category_id = NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_category.id"))
    user_id = NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_user.id"))  # 当前新闻的作者id
    status = NewsDB.Column(NewsDB.Integer, default=0)  # 当前新闻状态 如果为0代表审核通过，1代表审核中，-1代表审核不通过
    reason = NewsDB.Column(NewsDB.String(256))  # 未通过原因，status = -1 的时候使用
    # 当前新闻的所有评论
    comments = NewsDB.relationship("Comment", lazy="dynamic")

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
            "index_image_url": self.index_image_url if self.index_image_url else "",
            "author": self.user.to_dict() if self.user else None
        }
        return resp_dict


class Comment(BaseModel, NewsDB.Model):
    """评论"""
    __tablename__ = "info_comment"

    id = NewsDB.Column(NewsDB.Integer, primary_key=True)  # 评论编号
    user_id = NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_user.id"), nullable=False)  # 用户id
    news_id = NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_news.id"), nullable=False)  # 新闻id
    content = NewsDB.Column(NewsDB.Text, nullable=False)  # 评论内容
    parent_id = NewsDB.Column(NewsDB.Integer, NewsDB.ForeignKey("info_comment.id"))  # 父评论id
    parent = NewsDB.relationship("Comment", remote_side=[id])  # 自关联
    like_count = NewsDB.Column(NewsDB.Integer, default=0)  # 点赞条数

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "parent": self.parent.to_dict() if self.parent else None,
            "user": User.query.get(self.user_id).to_dict(),
            "news_id": self.news_id,
            "like_count": self.like_count
        }
        return resp_dict


class CommentLike(BaseModel, NewsDB.Model):
    """评论点赞"""
    __tablename__ = "info_comment_like"
    comment_id = NewsDB.Column("comment_id", NewsDB.Integer, NewsDB.ForeignKey("info_comment.id"), primary_key=True)  # 评论编号
    user_id = NewsDB.Column("user_id", NewsDB.Integer, NewsDB.ForeignKey("info_user.id"), primary_key=True)  # 用户编号


class Category(BaseModel, NewsDB.Model):
    """新闻分类"""
    __tablename__ = "info_category"

    id = NewsDB.Column(NewsDB.Integer, primary_key=True)  # 分类编号
    name = NewsDB.Column(NewsDB.String(64), nullable=False)  # 分类名
    news_list = NewsDB.relationship('News', backref='category', lazy='dynamic')

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name
        }
        return resp_dict
