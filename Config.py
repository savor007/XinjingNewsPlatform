from redis import StrictRedis
import logging



class AppsConfiguration():
    DEBUG=False
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
    LOG_LEVEL=logging.INFO


class AppsTestConfiguration(AppsConfiguration):
    DEBUG = True
    TESTING=True


class AppsDevelopmentConfig(AppsConfiguration):
    DEBUG = True


class OnlineProduction(AppsConfiguration):
    DEBUG = False


RunningConfig={
    "BaseConfig":AppsConfiguration,
    "Development":AppsDevelopmentConfig,
    "Testing":AppsTestConfiguration,
    "Online":OnlineProduction
}