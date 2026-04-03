from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default="farmer")
    district = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    farmer_profile = db.relationship("FarmerProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    crop_reports = db.relationship("CropReport", backref="farmer", lazy=True, cascade="all, delete-orphan")
    produce_listings = db.relationship("ProduceListing", backref="farmer", lazy=True, cascade="all, delete-orphan")
    farm_activities = db.relationship("FarmActivity", backref="farmer", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FarmerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    farm_size = db.Column(db.String(50))
    farm_location = db.Column(db.String(150))
    main_crops = db.Column(db.String(255))
    preferred_language = db.Column(db.String(50))
    farming_type = db.Column(db.String(50))

class CropReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    symptom_description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    suspected_issue = db.Column(db.String(150))
    recommendation = db.Column(db.Text)
    status = db.Column(db.String(50), default="pending")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProduceListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    harvest_date = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FarmActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    activity_date = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)

class Advisory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80))
    district = db.Column(db.String(100))
    created_by = db.Column(db.String(100), default="Admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class BuyerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("produce_listing.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="pending")
    approved_by_farmer = db.Column(db.Boolean, default=False)
    rejected_by_farmer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    buyer = db.relationship("User", backref="buyer_requests")
    listing = db.relationship("ProduceListing", backref="buyer_requests")
    
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.String(50), nullable=False)
    buyer_name = db.Column(db.String(120))
    
class ExtensionNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    extension_worker_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    crop_report_id = db.Column(db.Integer, db.ForeignKey("crop_report.id"), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    extension_worker = db.relationship("User", backref="extension_notes")
    crop_report = db.relationship("CropReport", backref="extension_notes")