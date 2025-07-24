import uuid
from pathlib import Path

import requests
import requests.exceptions
from apps.app import db
from apps.crud.models import User

from apps.classifier.forms import DeleteForm, UploadImageForm
from apps.classifier.models import UserImage, UserImageTag
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

classifier = Blueprint("classifier", __name__, template_folder="templates")

@classifier.route("/")
def index():
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    user_image_tag_dict = {}
    for user_image in user_images:
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id == user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

    delete_form = DeleteForm()

    return render_template(
        "classifier/index.html",
        user_images=user_images,
        user_image_tag_dict=user_image_tag_dict,
        delete_form=delete_form,
    )

@classifier.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@classifier.route("/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    form = UploadImageForm()
    if form.validate_on_submit():
        file = form.image.data
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)

        # Save image info to DB
        user_image = UserImage(user_id=current_user.id, image_path=image_uuid_file_name)
        try:
            db.session.add(user_image)
            db.session.commit()
            current_app.logger.info(f'Image uploaded by user {current_user.id}: {image_uuid_file_name}')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Database error saving image: {str(e)}')
            flash('画像の保存に失敗しました。')
            return redirect(url_for('classifier.upload_image'))

        # Send image to prediction API
        try:
            with open(image_path, "rb") as img_file:
                files = {"image": (image_uuid_file_name, img_file, file.mimetype)}
                headers = {"X-API-Key": current_app.config['API_KEY']}
                # Use API URL from configuration
                api_url = f"{current_app.config['API_BASE_URL']}/predict"
                response = requests.post(api_url, files=files, headers=headers)
            if response.ok:
                result = response.json()
                predicted_class = result.get("predicted_class")
                if predicted_class:
                    user_image_tag = UserImageTag(
                        user_image_id=user_image.id, tag_name=predicted_class
                    )
                    db.session.add(user_image_tag)
                    db.session.commit()
            else:
                current_app.logger.warning(f'API call failed with status {response.status_code}: {response.text}')
                flash(f'画像分類APIの呼び出しに失敗しました。(ステータス: {response.status_code})')
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'API request failed: {str(e)}')
            flash('画像分類APIへの接続に失敗しました。APIサーバーが停止している可能性があります。')
        except Exception as e:
            current_app.logger.error(f'Unexpected error during API call: {str(e)}')
            flash('画像分類処理で予期しないエラーが発生しました。')

        return redirect(url_for("classifier.index"))
    return render_template("classifier/upload.html", form=form)

@classifier.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        # Check if image belongs to current user
        user_image = UserImage.query.filter_by(id=image_id, user_id=current_user.id).first()
        if not user_image:
            flash('指定された画像が見つからないか、削除権限がありません。')
            return redirect(url_for('classifier.index'))
        
        # Delete tags first, then image
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()
        db.session.commit()
        
        current_app.logger.info(f'Image {image_id} deleted by user {current_user.id}')
        flash('画像を削除しました。')
        
    except Exception as e:
        flash('画像削除処理でエラーが発生しました。')
        current_app.logger.error(f'Error deleting image {image_id}: {str(e)}')
        db.session.rollback()
    return redirect(url_for("classifier.index"))