import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
from config import config_by_name

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

def create_app():
    env = os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.farmer import farmer_bp
    from app.routes.marketplace import marketplace_bp
    from app.routes.advisory import advisory_bp
    from app.routes.admin import admin_bp
    from app.routes.buyer import buyer_bp
    from app.routes.notifications import notifications_bp
    from app.routes.extension import extension_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(advisory_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(extension_bp)
    app.register_blueprint(api_bp)

    return app