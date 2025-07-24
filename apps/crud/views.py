from apps.app import db
from apps.crud.forms import UserForm
from apps.crud.models import User
from flask import Blueprint, redirect, render_template, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps

# Blueprintでcrudアプリを生成する
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# 管理者権限チェックデコレータ
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('管理者権限が必要です')
            return redirect(url_for('classifier.index'))
        return f(*args, **kwargs)
    return decorated_function


# 自分または管理者のみアクセス可能なデコレータ
def self_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not (current_user.is_admin() or current_user.is_current_user(user_id)):
            flash('アクセス権限がありません')
            return redirect(url_for('classifier.index'))
        return f(*args, **kwargs)
    return decorated_function


# indexエンドポイントを作成しindex.htmlを返す
@crud.route("/")
@login_required
@admin_required
def index():
    # 管理者にはユーザー一覧を表示
    return redirect(url_for('crud.users'))


@crud.route("/sql")
@login_required
def sql():
    db.session.query(User).all()
    return "コンソールログを確認してください"


@crud.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    # UserFormをインスタンス化する
    form = UserForm()

    # フォームの値をバリデートする
    if form.validate_on_submit():
        # ユーザーを作成する
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        # ユーザーを追加してコミットする
        db.session.add(user)
        db.session.commit()

        # ユーザーの一覧画面へリダイレクトする
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)


@crud.route("/users")
@login_required
@admin_required
def users():
    """ユーザーの一覧を取得する"""
    users = User.query.all()
    return render_template("crud/index.html", users=users)


# methodsにGETとPOSTを指定する
@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required
@self_or_admin_required
def edit_user(user_id):
    form = UserForm()

    # Userモデルを利用してユーザーを取得する
    user = User.query.filter_by(id=user_id).first()

    # formからサブミットされた場合はユーザーを更新しユーザーの一覧画面へリダイレクトする
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))

    # GETの場合はHTMLを返す
    return render_template("crud/edit.html", user=user, form=form)


@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    
    # 自分自身の削除を防ぐ
    if current_user.is_current_user(user_id):
        flash('自分自身を削除することはできません')
        return redirect(url_for("crud.users"))
    
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'ユーザー {user.username} を削除しました')
    else:
        flash('ユーザーが見つかりません')
    
    return redirect(url_for("crud.users"))


# ユーザープロフィール管理
@crud.route("/profile")
@login_required
def profile():
    """現在のユーザーのプロフィールを表示"""
    return render_template("crud/profile.html", user=current_user)


@crud.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """現在のユーザーのプロフィールを編集"""
    form = UserForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:  # パスワードが入力された場合のみ更新
            current_user.password = form.password.data
        db.session.commit()
        flash('プロフィールを更新しました')
        return redirect(url_for("crud.profile"))
    
    return render_template("crud/edit_profile.html", user=current_user, form=form)
