from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField, TextAreaField,
    FloatField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    district = StringField("District", validators=[Optional(), Length(max=100)])
    role = SelectField("Role", choices=[
        ("farmer", "Farmer"),
        ("buyer", "Buyer"),
        ("extension_worker", "Extension Worker")
    ], validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password")
    ])
    submit = SubmitField("Create Account")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class FarmerProfileForm(FlaskForm):
    farm_size = StringField("Farm Size")
    farm_location = StringField("Farm Location")
    main_crops = StringField("Main Crops")
    preferred_language = StringField("Preferred Language")
    farming_type = SelectField("Farming Type", choices=[
        ("subsistence", "Subsistence"),
        ("commercial", "Commercial"),
        ("mixed", "Mixed")
    ])
    submit = SubmitField("Save Profile")

class CropReportForm(FlaskForm):
    crop_name = StringField("Crop Name", validators=[DataRequired()])
    symptom_description = TextAreaField("Symptoms", validators=[DataRequired()])
    image = FileField("Crop Image", validators=[
        Optional(),
        FileAllowed(["jpg", "jpeg", "png"], "Images only!")
    ])
    submit = SubmitField("Submit Report")

class ProduceListingForm(FlaskForm):
    crop_name = StringField("Crop Name", validators=[DataRequired()])
    quantity = FloatField("Quantity", validators=[DataRequired()])
    unit = SelectField("Unit", choices=[
        ("kg", "kg"),
        ("bags", "bags"),
        ("tons", "tons"),
        ("crates", "crates")
    ], validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    harvest_date = StringField("Harvest Date")
    description = TextAreaField("Description")
    submit = SubmitField("Create Listing")

class FarmActivityForm(FlaskForm):
    crop_name = StringField("Crop Name", validators=[DataRequired()])
    activity_type = SelectField("Activity Type", choices=[
        ("planting", "Planting"),
        ("weeding", "Weeding"),
        ("spraying", "Spraying"),
        ("fertilizer", "Fertilizer"),
        ("harvesting", "Harvesting"),
        ("other", "Other")
    ], validators=[DataRequired()])
    activity_date = StringField("Activity Date", validators=[DataRequired()])
    cost = FloatField("Cost", validators=[Optional()], default=0)
    notes = TextAreaField("Notes")
    submit = SubmitField("Save Record")

class AdvisoryForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    category = StringField("Category", validators=[Optional()])
    district = StringField("District", validators=[Optional()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post Advisory")
    

    
class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")

class ApproveBuyerRequestForm(FlaskForm):
    submit = SubmitField("Approve")

class RejectBuyerRequestForm(FlaskForm):
    submit = SubmitField("Reject")

class ExtensionNoteForm(FlaskForm):
    note = TextAreaField("Advice / Note", validators=[DataRequired()])
    submit = SubmitField("Submit Note")

class SaleForm(FlaskForm):
    crop_name = StringField("Crop Name", validators=[DataRequired()])
    quantity = FloatField("Quantity", validators=[DataRequired()])
    unit = SelectField("Unit", choices=[
        ("kg", "kg"),
        ("bags", "bags"),
        ("tons", "tons"),
        ("crates", "crates")
    ], validators=[DataRequired()])
    unit_price = FloatField("Unit Price", validators=[DataRequired()])
    sale_date = StringField("Sale Date", validators=[DataRequired()])
    buyer_name = StringField("Buyer Name", validators=[Optional()])
    submit = SubmitField("Save Sale")