from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from flask_login import login_required, current_user
from app import db
from app.decorators import roles_required
from app.forms import ExtensionNoteForm
from app.models import CropReport, ExtensionNote, Notification
from math import ceil

extension_bp = Blueprint("extension", __name__, url_prefix="/extension")

@extension_bp.route("/dashboard")
@login_required
@roles_required("extension_worker")
def dashboard():
    page = 1
    per_page = 10
    pagination = CropReport.query.order_by(CropReport.submitted_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("extension/dashboard.html", pagination=pagination, reports=pagination.items)

@extension_bp.route("/crop-report/<int:report_id>/note", methods=["GET", "POST"])
@login_required
@roles_required("extension_worker")
def add_note(report_id):
    report = CropReport.query.get_or_404(report_id)
    form = ExtensionNoteForm()

    if form.validate_on_submit():
        note = ExtensionNote(
            extension_worker_id=current_user.id,
            crop_report_id=report.id,
            note=form.note.data
        )
        db.session.add(note)

        notification = Notification(
            user_id=report.farmer_id,
            title="Extension Worker Feedback",
            message=f"Your report for {report.crop_name} has received expert guidance."
        )
        db.session.add(notification)

        db.session.commit()
        flash("Extension note submitted.", "success")
        return redirect(url_for("extension.dashboard"))

    return render_template("extension/add_note.html", form=form, report=report)