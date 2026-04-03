from flask import Blueprint, render_template
from app.models import ProduceListing, Advisory

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    recent_listings = ProduceListing.query.order_by(ProduceListing.created_at.desc()).limit(6).all()
    advisories = Advisory.query.order_by(Advisory.created_at.desc()).limit(4).all()
    return render_template("index.html", recent_listings=recent_listings, advisories=advisories)