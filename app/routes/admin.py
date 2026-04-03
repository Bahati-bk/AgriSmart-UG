from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.decorators import roles_required
from app.forms import AdvisoryForm
from app.models import User, CropReport, ProduceListing, Advisory, FarmActivity

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def dashboard():
    form = AdvisoryForm()

    if form.validate_on_submit():
        advisory = Advisory(
            title=form.title.data,
            category=form.category.data,
            district=form.district.data,
            content=form.content.data,
            created_by="Admin"
        )
        db.session.add(advisory)
        db.session.commit()
        flash("Advisory posted successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    users_count = User.query.count()
    reports_count = CropReport.query.count()
    listings_count = ProduceListing.query.count()
    activities_count = FarmActivity.query.count()
    recent_reports = CropReport.query.order_by(CropReport.submitted_at.desc()).limit(5).all()

    crop_report_counts = {}
    for report in CropReport.query.all():
        crop_report_counts[report.crop_name] = crop_report_counts.get(report.crop_name, 0) + 1

    listing_counts = {}
    for listing in ProduceListing.query.all():
        listing_counts[listing.crop_name] = listing_counts.get(listing.crop_name, 0) + 1

    return render_template(
        "admin/dashboard.html",
        form=form,
        users_count=users_count,
        reports_count=reports_count,
        listings_count=listings_count,
        activities_count=activities_count,
        recent_reports=recent_reports,
        crop_chart_labels=list(crop_report_counts.keys()),
        crop_chart_values=list(crop_report_counts.values()),
        listing_chart_labels=list(listing_counts.keys()),
        listing_chart_values=list(listing_counts.values())
    )