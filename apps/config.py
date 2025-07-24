import os
from pathlib import Path

basedir = Path(__file__).parent.parent


# BaseConfigクラスを作成する
class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5001')
    API_KEY = os.environ.get('API_KEY')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(Path(basedir, "apps", "images"))
    
    @staticmethod
    def validate_config():
        """Validate required configuration"""
        if not BaseConfig.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        if not BaseConfig.API_KEY:
            raise ValueError("API_KEY environment variable is required")
    
# BaseConfigクラスを継承してLocalConfigクラスを作成する
class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    
    # Development environment allows fallback values
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    API_KEY = os.environ.get('API_KEY') or 'dev-api-key-change-in-production'


# BaseConfigクラスを継承してTestingConfigクラスを作成する
class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    # 画像アップロード先にtests/classifier/imagesを指定する
    UPLOAD_FOLDER = str(Path(basedir, "tests", "classifier", "images"))


# BaseConfigクラスを継承してProductionConfigクラスを作成する
class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{basedir / 'production.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    # 画像アップロード先を環境変数から設定
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(Path(basedir, "uploads"))


# config辞書にマッピングする
config = {
    "testing": TestingConfig,
    "local": LocalConfig,
    "production": ProductionConfig,
}