class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Axm022425!!@localhost/mechanic_shop_db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300 # 5 minutes
    
class TestingConfig:
    pass

class ProductionConfig:
    pass