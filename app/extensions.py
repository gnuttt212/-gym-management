"""Lazy-initialized extensions – bound to app in create_app()."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
sess = Session()
csrf = CSRFProtect()

# Redis client – set in create_app()
redis_client = None
