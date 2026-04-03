from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.decorators import roles_required
from app.models import ProduceListing, BuyerRequest, Notification

buyer_bp = Blueprint("buyer", __name__, url_prefix="/buyer")

@buyer_bp.route("/dashboard")
@login_required
@roles_required("buyer")
def dashboard():
    requests_made = BuyerRequest.query.filter_by(buyer_id=current_user.id).order_by(BuyerRequest.created_at.desc()).all()
    listings = ProduceListing.query.order_by(ProduceListing.created_at.desc()).limit(8).all()
    return render_template("buyer/dashboard.html", requests_made=requests_made, listings=listings)

@buyer_bp.route("/listing/<int:listing_id>/request", methods=["GET", "POST"])
@login_required
@roles_required("buyer")
def request_listing(listing_id):
    listing = ProduceListing.query.get_or_404(listing_id)
    form = BuyerRequestForm() # type: ignore

    if form.validate_on_submit():
        buyer_request = BuyerRequest(
            buyer_id=current_user.id,
            listing_id=listing.id,
            message=form.message.data
        )
        db.session.add(buyer_request)

        notification = Notification(
            user_id=listing.farmer_id,
            title="New Buyer Request",
            message=f"{current_user.full_name} is interested in your {listing.crop_name} listing."
        )
        db.session.add(notification)

        db.session.commit()
        flash("Your request has been sent to the farmer.", "success")
        return redirect(url_for("buyer.dashboard"))

    return render_template("buyer/request_listing.html", form=form, listing=listing)