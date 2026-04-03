from flask import Blueprint, render_template, request
from app.models import Advisory

advisory_bp = Blueprint("advisory", __name__, url_prefix="/advisories")

@advisory_bp.route("/")
def list_advisories():
    district = request.args.get("district", "").strip()

    query = Advisory.query
    if district:
        query = query.filter(
            (Advisory.district == district) | (Advisory.district == None) | (Advisory.district == "")
        )

    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Advisory.created_at.desc()).paginate(page=page, per_page=6, error_out=False)

    districts = sorted({a.district for a in Advisory.query.all() if a.district})
    return render_template(
        "advisory/advisories.html",
        advisories=pagination.items,
        pagination=pagination,
        districts=districts,
        selected_district=district
    )