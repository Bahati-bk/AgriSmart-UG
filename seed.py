from app import create_app, db
from app.models import User, FarmerProfile, ProduceListing, Advisory, FarmActivity, CropReport, Notification
from app.models import User, FarmerProfile, ProduceListing, Advisory, FarmActivity, CropReport, Notification, Sale

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(full_name="Admin User", email="admin@agrismart.com", role="admin", district="Kampala")
    admin.set_password("admin123")

    farmer = User(full_name="Sarah Nankya", email="farmer@agrismart.com", role="farmer", district="Mukono")
    farmer.set_password("password123")

    buyer = User(full_name="Kato Produce Buyers", email="buyer@agrismart.com", role="buyer", district="Kampala")
    buyer.set_password("password123")

    db.session.add_all([admin, farmer, buyer])
    db.session.commit()

    profile = FarmerProfile(
        user_id=farmer.id,
        farm_size="3 acres",
        farm_location="Mukono",
        main_crops="Maize, Beans, Tomatoes",
        preferred_language="English",
        farming_type="mixed"
    )
    db.session.add(profile)

    listing1 = ProduceListing(
        farmer_id=farmer.id,
        crop_name="Maize",
        quantity=500,
        unit="kg",
        price=1200,
        location="Mukono",
        harvest_date="2026-04-10",
        description="Dry maize ready for sale"
    )
    listing2 = ProduceListing(
        farmer_id=farmer.id,
        crop_name="Beans",
        quantity=200,
        unit="kg",
        price=3500,
        location="Mukono",
        harvest_date="2026-04-15",
        description="Clean beans available"
    )

    advisory1 = Advisory(
        title="Prepare for Rainy Season",
        content="Farmers are advised to prepare seed beds early and ensure drainage channels are clear.",
        category="Weather",
        district="Mukono",
        created_by="Admin"
    )

    activity1 = FarmActivity(
        farmer_id=farmer.id,
        crop_name="Maize",
        activity_type="planting",
        activity_date="2026-03-20",
        cost=120000,
        notes="Planted hybrid maize seeds"
    )

    report1 = CropReport(
        farmer_id=farmer.id,
        crop_name="Tomatoes",
        symptom_description="Yellowing leaves and spots",
        suspected_issue="Possible fungal infection",
        recommendation="Remove affected leaves and apply a fungicide.",
        status="reviewed"
    )
    
    extension = User(full_name="Grace Extension", email="extension@agrismart.com", role="extension_worker", district="Mukono")
    extension.set_password("password123")
    db.session.add(extension)
    db.session.commit()
    
    sale1 = Sale(
    farmer_id=farmer.id,
    crop_name="Maize",
    quantity=100,
    unit="kg",
    unit_price=1200,
    total_amount=120000,
    sale_date="2026-04-03",
    buyer_name="Kampala Grain Traders"
    )
    db.session.add(sale1)

    notification1 = Notification(
        user_id=farmer.id,
        title="Welcome to AgriSmart UG",
        message="Your account has been created successfully."
    )

    db.session.add_all([listing1, listing2, advisory1, activity1, report1, notification1])
    db.session.commit()

    print("Seed data inserted successfully.")