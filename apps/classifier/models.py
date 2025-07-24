from datetime import datetime

from apps.app import db


class UserImage(db.Model):
    __tablename__ = "user_images"
    id = db.Column(db.Integer, primary_key=True)
    # user_idはusersテーブルのidカラムを外部キーとして設定する
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    is_detected = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('images', lazy=True, cascade='all, delete-orphan'))
    tags = db.relationship('UserImageTag', backref='image', lazy=True, cascade='all, delete-orphan')


class UserImageTag(db.Model):
    # テーブル名を指定する
    __tablename__ = "user_image_tags"
    id = db.Column(db.Integer, primary_key=True)
    # user_image_idはuser_imagesテーブルのidカラムの外部キーとして設定する
    user_image_id = db.Column(db.Integer, db.ForeignKey("user_images.id"), nullable=False, index=True)
    tag_name = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
