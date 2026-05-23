from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'    

    @app.context_processor
    def inject_unread_count():
        from flask_login import current_user
        if current_user.is_authenticated:
            from app.models import Notification
            count = Notification.query.filter_by(
                user_id=current_user.user_id,
                is_read=False
            ).count()
            return {'unread_count': count}
        return {'unread_count': 0}    

    with app.app_context():
        from app import models

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)

    from app.matching import matching as matching_blueprint
    app.register_blueprint(matching_blueprint)
    
    from app.requests import requests_bp as requests_blueprint
    app.register_blueprint(requests_blueprint)
    
    from app.notifications import notifications as notifications_blueprint
    app.register_blueprint(notifications_blueprint)

    from app.ratings import ratings as ratings_blueprint
    app.register_blueprint(ratings_blueprint)

    from app.messages import messages as messages_blueprint
    app.register_blueprint(messages_blueprint)

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from app.skills import skills as skills_blueprint
    app.register_blueprint(skills_blueprint)

    return app


