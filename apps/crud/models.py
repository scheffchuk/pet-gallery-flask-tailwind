from datetime import datetime

from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


# db.Modelを継承したUserクラスを作成する
class User(db.Model, UserMixin):
    # テーブル名を指定する
    __tablename__ = "users"
    # カラムを定義する
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False, index=True)  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # パスワードをセットするためのプロパティ
    @property
    def password(self):
        raise AttributeError("読み取り不可")

    # パスワードをセットするためのセッター関数でハッシュ化したパスワードをセットする
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # パスワードチェックをする
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # メールアドレス重複チェックをする
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    
    # 管理者権限チェック
    def is_admin(self):
        return self.role == 'admin'
    
    # ユーザーが自分自身かどうかチェック
    def is_current_user(self, user_id):
        return str(self.id) == str(user_id)


# ログインしているユーザー情報を取得する関数を作成する
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
