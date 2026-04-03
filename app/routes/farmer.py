import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_file, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.decorators import roles_required
from app.forms import (
    ApproveBuyerRequestForm, DeleteForm, FarmerProfileForm, CropReportForm, FarmActivityForm,
    ProduceListingForm, RejectBuyerRequestForm, SaleForm
)
from app.models import (
    FarmerProfile, CropReport, FarmActivity, 
    ProduceListing, Notification, BuyerRequest, Sale
)
import io
import csv
from reportlab.pdfgen import canvas

from app.services.ml_diagnosis import predict_crop_image
from app.services.sms import send_sms
from app.services.weather import get_weather_by_district


farmer_bp = Blueprint("farmer", __name__, url_prefix="/farmer")

def simple_diagnosis(symptoms: str):
    text = symptoms.lower()

    if "yellow" in text or "wilting" in text:
        return "Possible nutrient deficiency", "Apply appropriate fertilizer and inspect soil health."
    if "spots" in text or "fungus" in text:
        return "Possible fungal infection", "Remove affected leaves and consider a recommended fungicide."
    if "holes" in text or "eaten" in text:
        return "Possible pest attack", "Inspect plants for pests and apply suitable pest control."
    return "General crop stress", "Consult an extension worker and monitor the crop closely."

@farmer_bp.route("/dashboard")
@login_required
@roles_required("farmer")
def dashboard():
    reports_count = CropReport.query.filter_by(farmer_id=current_user.id).count()
    listings_count = ProduceListing.query.filter_by(farmer_id=current_user.id).count()
    activities_count = FarmActivity.query.filter_by(farmer_id=current_user.id).count()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    weather = get_weather_by_district(current_user.district)

    return render_template(
        "farmer/dashboard.html",
        reports_count=reports_count,
        listings_count=listings_count,
        activities_count=activities_count,
        notifications=notifications,
        weather=weather
    )

@farmer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def profile():
    profile = current_user.farmer_profile
    form = FarmerProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.farm_size = form.farm_size.data
        profile.farm_location = form.farm_location.data
        profile.main_crops = form.main_crops.data
        profile.preferred_language = form.preferred_language.data
        profile.farming_type = form.farming_type.data
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("farmer.profile"))

    return render_template("farmer/profile.html", form=form)

@farmer_bp.route("/crop-report/new", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def new_crop_report():
    form = CropReportForm()

    if form.validate_on_submit():
        image_path = None

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
            form.image.data.save(save_path)
            image_path = f"uploads/{unique_name}"

        suspected_issue, recommendation = simple_diagnosis(form.symptom_description.data)

    if image_path:
        ml_result = predict_crop_image(save_path)
        if ml_result["confidence"] > 0.6:
            suspected_issue = ml_result["label"]
            recommendation = ml_result["recommendation"]

        report = CropReport(
            farmer_id=current_user.id,
            crop_name=form.crop_name.data,
            symptom_description=form.symptom_description.data,
            image_path=image_path,
            suspected_issue=suspected_issue,
            recommendation=recommendation,
            status="reviewed"
        )
        db.session.add(report)

        notification = Notification(
            user_id=current_user.id,
            title="Crop Report Feedback",
            message=f"Your report for {form.crop_name.data} was reviewed. Suggested issue: {suspected_issue}."
        )
        db.session.add(notification)

        db.session.commit()
        flash("Crop report submitted successfully.", "success")
        return redirect(url_for("farmer.crop_reports"))

    return render_template("farmer/crop_report_form.html", form=form)

@farmer_bp.route("/crop-reports")
@login_required
@roles_required("farmer")
def crop_reports():
    from flask import request
    page = request.args.get("page", 1, type=int)
    pagination = CropReport.query.filter_by(farmer_id=current_user.id).order_by(
    CropReport.submitted_at.desc()
    ).paginate(page=page, per_page=5, error_out=False)
    delete_form = DeleteForm()

    return render_template("farmer/crop_reports.html", reports=pagination.items, pagination=pagination, delete_form=delete_form)

@farmer_bp.route("/crop-report/<int:report_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def edit_crop_report(report_id):
    report = CropReport.query.get_or_404(report_id)
    if report.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.crop_reports"))

    form = CropReportForm(obj=report)
    if form.validate_on_submit():
        report.crop_name = form.crop_name.data
        report.symptom_description = form.symptom_description.data
        report.suspected_issue, report.recommendation = simple_diagnosis(form.symptom_description.data)
        db.session.commit()
        flash("Crop report updated successfully.", "success")
        return redirect(url_for("farmer.crop_reports"))

    return render_template("farmer/edit_crop_report.html", form=form)

@farmer_bp.route("/crop-report/<int:report_id>/delete", methods=["POST"])
@login_required
@roles_required("farmer")
def delete_crop_report(report_id):
    form = DeleteForm()
    if not form.validate_on_submit():
        flash("Invalid delete request.", "danger")
        return redirect(url_for("farmer.crop_reports"))
    report = CropReport.query.get_or_404(report_id)
    if report.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.crop_reports"))

    db.session.delete(report)
    db.session.commit()
    flash("Crop report deleted.", "info")
    return redirect(url_for("farmer.crop_reports"))

@farmer_bp.route("/farm-records")
@login_required
@roles_required("farmer")
def farm_records():
    records = FarmActivity.query.filter_by(farmer_id=current_user.id).order_by(FarmActivity.id.desc()).all()
    return render_template("farmer/farm_records.html", records=records)

@farmer_bp.route("/farm-records/new", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def add_farm_record():
    form = FarmActivityForm()
    if form.validate_on_submit():
        record = FarmActivity(
            farmer_id=current_user.id,
            crop_name=form.crop_name.data,
            activity_type=form.activity_type.data,
            activity_date=form.activity_date.data,
            cost=form.cost.data or 0,
            notes=form.notes.data
        )
        db.session.add(record)
        db.session.commit()
        flash("Farm record added successfully.", "success")
        return redirect(url_for("farmer.farm_records"))

    return render_template("farmer/add_farm_record.html", form=form)

@farmer_bp.route("/farm-record/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def edit_farm_record(record_id):
    record = FarmActivity.query.get_or_404(record_id)
    if record.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.farm_records"))

    form = FarmActivityForm(obj=record)
    if form.validate_on_submit():
        record.crop_name = form.crop_name.data
        record.activity_type = form.activity_type.data
        record.activity_date = form.activity_date.data
        record.cost = form.cost.data or 0
        record.notes = form.notes.data
        db.session.commit()
        flash("Farm record updated successfully.", "success")
        return redirect(url_for("farmer.farm_records"))

    return render_template("farmer/edit_farm_record.html", form=form)

@farmer_bp.route("/farm-record/<int:record_id>/delete", methods=["POST"])
@login_required
@roles_required("farmer")
def delete_farm_record(record_id):
    record = FarmActivity.query.get_or_404(record_id)
    if record.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.farm_records"))

    db.session.delete(record)
    db.session.commit()
    flash("Farm record deleted.", "info")
    return redirect(url_for("farmer.farm_records"))


@farmer_bp.route("/buyer-requests")
@login_required
@roles_required("farmer")
def buyer_requests():
    requests = BuyerRequest.query.join(ProduceListing).filter(
        ProduceListing.farmer_id == current_user.id
    ).order_by(BuyerRequest.created_at.desc()).all()

    approve_forms = {req.id: ApproveBuyerRequestForm(prefix=f"approve-{req.id}") for req in requests}
    reject_forms = {req.id: RejectBuyerRequestForm(prefix=f"reject-{req.id}") for req in requests}

    return render_template(
        "farmer/buyer_requests.html",
        requests=requests,
        approve_forms=approve_forms,
        reject_forms=reject_forms
    )
    
@farmer_bp.route("/buyer-request/<int:request_id>/approve", methods=["POST"])
@login_required
@roles_required("farmer")
def approve_buyer_request(request_id):
    req = BuyerRequest.query.get_or_404(request_id)
    form = ApproveBuyerRequestForm(prefix=f"approve-{req.id}")

    if not form.validate_on_submit():
        flash("Invalid form submission.", "danger")
        return redirect(url_for("farmer.buyer_requests"))

    if req.listing.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.buyer_requests"))

    req.status = "approved"
    req.approved_by_farmer = True
    req.rejected_by_farmer = False

    notification = Notification(
        user_id=req.buyer_id,
        title="Request Approved",
        message=f"Your request for {req.listing.crop_name} has been approved by the farmer."
    )
    db.session.add(notification)
    db.session.commit()

    if req.buyer.phone:
        send_sms(req.buyer.phone, f"Your AgriSmart request for {req.listing.crop_name} was approved.")

    flash("Buyer request approved.", "success")
    return redirect(url_for("farmer.buyer_requests"))

@farmer_bp.route("/buyer-request/<int:request_id>/reject", methods=["POST"])
@login_required
@roles_required("farmer")
def reject_buyer_request(request_id):
    req = BuyerRequest.query.get_or_404(request_id)
    form = RejectBuyerRequestForm(prefix=f"reject-{req.id}")

    if not form.validate_on_submit():
        flash("Invalid form submission.", "danger")
        return redirect(url_for("farmer.buyer_requests"))

    if req.listing.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("farmer.buyer_requests"))

    req.status = "rejected"
    req.approved_by_farmer = False
    req.rejected_by_farmer = True

    notification = Notification(
        user_id=req.buyer_id,
        title="Request Rejected",
        message=f"Your request for {req.listing.crop_name} was not approved."
    )
    db.session.add(notification)
    db.session.commit()

    flash("Buyer request rejected.", "info")
    return redirect(url_for("farmer.buyer_requests"))

@farmer_bp.route("/sales", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def sales():
    form = SaleForm()
    if form.validate_on_submit():
        total_amount = (form.quantity.data or 0) * (form.unit_price.data or 0)
        sale = Sale(
            farmer_id=current_user.id,
            crop_name=form.crop_name.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            unit_price=form.unit_price.data,
            total_amount=total_amount,
            sale_date=form.sale_date.data,
            buyer_name=form.buyer_name.data
        )
        db.session.add(sale)
        db.session.commit()
        flash("Sale recorded successfully.", "success")
        return redirect(url_for("farmer.sales"))

    sales_list = Sale.query.filter_by(farmer_id=current_user.id).all()
    records = FarmActivity.query.filter_by(farmer_id=current_user.id).all()

    revenue_by_crop = {}
    for sale in sales_list:
        revenue_by_crop[sale.crop_name] = revenue_by_crop.get(sale.crop_name, 0) + sale.total_amount

    cost_by_crop = {}
    for record in records:
        cost_by_crop[record.crop_name] = cost_by_crop.get(record.crop_name, 0) + (record.cost or 0)

    crops = sorted(set(list(revenue_by_crop.keys()) + list(cost_by_crop.keys())))
    revenues = [revenue_by_crop.get(crop, 0) for crop in crops]
    costs = [cost_by_crop.get(crop, 0) for crop in crops]
    profits = [revenue_by_crop.get(crop, 0) - cost_by_crop.get(crop, 0) for crop in crops]

    return render_template(
        "farmer/sales.html",
        form=form,
        sales_list=sales_list,
        chart_labels=crops,
        chart_revenues=revenues,
        chart_costs=costs,
        chart_profits=profits
    )
    
@farmer_bp.route("/sales/export/csv")
@login_required
@roles_required("farmer")
def export_sales_csv():
    sales_list = Sale.query.filter_by(farmer_id=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Crop", "Quantity", "Unit", "Unit Price", "Total Amount", "Sale Date", "Buyer Name"])

    for sale in sales_list:
        writer.writerow([
            sale.crop_name,
            sale.quantity,
            sale.unit,
            sale.unit_price,
            sale.total_amount,
            sale.sale_date,
            sale.buyer_name or ""
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sales_report.csv"}
    )
    
@farmer_bp.route("/sales/export/pdf")
@login_required
@roles_required("farmer")
def export_sales_pdf():
    sales_list = Sale.query.filter_by(farmer_id=current_user.id).all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle("Sales Report")

    y = 800
    p.drawString(50, y, f"AgriSmart UG - Sales Report for {current_user.full_name}")
    y -= 30

    for sale in sales_list:
        line = f"{sale.crop_name} | {sale.quantity} {sale.unit} | UGX {sale.total_amount} | {sale.sale_date}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="sales_report.pdf",
        mimetype="application/pdf"
    )