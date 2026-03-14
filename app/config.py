import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(basedir)
load_dotenv(os.path.join(parent_dir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-por-defecto-insegura'
    db_path = os.path.join(parent_dir, 'valin.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
