from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notifications_bp.route("/")
@login_required
def list_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template("notifications/list.html", notifications=notifications)

@notifications_bp.route("/<int:notification_id>/read")
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)

    if notification.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("notifications.list_notifications"))

    notification.is_read = True
    db.session.commit()
    flash("Notification marked as read.", "success")
    return redirect(url_for("notifications.list_notifications"))

@notifications_bp.route("/read-all")
@login_required
def mark_all_as_read():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("notifications.list_notifications"))