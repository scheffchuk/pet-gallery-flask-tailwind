import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from apps.config import config

# Load environment variables
load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
# LoginManagerをインスタンス化する
login_manager = LoginManager()
# login_view属性に未ログイン時にリダイレクトするエンドポイントを指定する
login_manager.login_view = "auth.signup"
# login_message属性にログイン後に表示するメッセージを指定する
# ここでは何も表示しないよう空を指定する
login_manager.login_message = ""


def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Set up file logging
        file_handler = RotatingFileHandler(
            'logs/dcc_app.log', maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('DCC App startup')


# create_app関数を作成する
def create_app(config_key):
    # Flaskインスタンス生成
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(config[config_key])

    # SQLAlchemyとアプリを連携する
    db.init_app(app)
    # Migrateとアプリを連携する
    Migrate(app, db)
    csrf.init_app(app)
    # login_managerをアプリケーションと連携する
    login_manager.init_app(app)
    
    # Configure logging
    configure_logging(app)

    # crudパッケージからviewsをimportする
    from apps.crud import views as crud_views

    # register_blueprintを使いviewsのcrudをアプリへ登録する
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # これから作成するauthパッケージからviewsをimportする
    from apps.auth import views as auth_views

    # register_blueprintを使いviewsのauthをアプリへ登録する
    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    # これから作成するclassifierパッケージからviewsをimportする
    from apps.classifier import views as classifier_views

    # register_blueprintを使いviewsのclassifierをアプリへ登録する
    app.register_blueprint(classifier_views.classifier)

    return app