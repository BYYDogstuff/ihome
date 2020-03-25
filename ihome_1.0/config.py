import redis

class Config(object):
    '''配置信息'''

    SECRET_KEY = 'xiaobaihenyuanya'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask_session配置
    SESSION_TYPE = 'redis'  # 指定要使用的会话接口的类型
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中的session_id进行隐藏(是否签名会话cookie sid，如果设置为True，则必须设置 flask.Flask.secret_key，默认为 False)
    PERMANENT_SESSION_LIFETIME = 86400 # session数据的有效期，一天


class DevelopmentConfig(Config):
    '''开发模式的配置信息'''
    DEBUG = True

class ProductionConfig(Config):
    '''生产环境配置信息'''
    pass

config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
