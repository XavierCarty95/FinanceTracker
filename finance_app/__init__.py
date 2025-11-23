# for finance_app
from flask import Flask, redirect, url_for   # 👈 add redirect, url_for
from dotenv import load_dotenv
import os
from finance_app.database import Base, engine
import finance_app.models
from finance_app import *

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    from .routes_onboarding import onboarding_bp
    from .routes_dashboard import dashboard_bp

    app.register_blueprint(onboarding_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        # send user to the new account page (or dashboard if logged in)
        return redirect(url_for("onboarding.new_account"))

    return app
