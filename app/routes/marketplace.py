from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms import ProduceListingForm
from app.models import ProduceListing
from app.decorators import roles_required

marketplace_bp = Blueprint("marketplace", __name__, url_prefix="/marketplace")

@marketplace_bp.route("/")
def listings():
    q = request.args.get("q", "").strip()
    if q:
        listings = ProduceListing.query.filter(
            ProduceListing.crop_name.ilike(f"%{q}%")
        ).order_by(ProduceListing.created_at.desc()).all()
    else:
        listings = ProduceListing.query.order_by(ProduceListing.created_at.desc()).all()

    return render_template("marketplace/listings.html", listings=listings, q=q)

@marketplace_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def create_listing():
    form = ProduceListingForm()
    if form.validate_on_submit():
        listing = ProduceListing(
            farmer_id=current_user.id,
            crop_name=form.crop_name.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            price=form.price.data,
            location=form.location.data,
            harvest_date=form.harvest_date.data,
            description=form.description.data
        )
        db.session.add(listing)
        db.session.commit()
        flash("Produce listing created successfully.", "success")
        return redirect(url_for("marketplace.listings"))

    return render_template("marketplace/create_listing.html", form=form)

@marketplace_bp.route("/<int:listing_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("farmer")
def edit_listing(listing_id):
    listing = ProduceListing.query.get_or_404(listing_id)
    if listing.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("marketplace.listings"))

    form = ProduceListingForm(obj=listing)
    if form.validate_on_submit():
        listing.crop_name = form.crop_name.data
        listing.quantity = form.quantity.data
        listing.unit = form.unit.data
        listing.price = form.price.data
        listing.location = form.location.data
        listing.harvest_date = form.harvest_date.data
        listing.description = form.description.data
        db.session.commit()
        flash("Listing updated successfully.", "success")
        return redirect(url_for("marketplace.listings"))

    return render_template("marketplace/edit_listing.html", form=form)

@marketplace_bp.route("/<int:listing_id>/delete", methods=["POST"])
@login_required
@roles_required("farmer")
def delete_listing(listing_id):
    listing = ProduceListing.query.get_or_404(listing_id)
    if listing.farmer_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("marketplace.listings"))

    db.session.delete(listing)
    db.session.commit()
    flash("Listing deleted.", "info")
    return redirect(url_for("marketplace.listings"))