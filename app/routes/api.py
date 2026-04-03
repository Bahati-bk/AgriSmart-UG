from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.services.weather import get_weather_by_district

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/weather")
@login_required
def weather():
    weather_data = get_weather_by_district(current_user.district)
    if not weather_data:
        return jsonify({"success": False, "message": "Weather unavailable"}), 404
    return jsonify({"success": True, "data": weather_data})