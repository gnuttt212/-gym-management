import os
import redis as redis_lib
from flask import Flask

from .config import config_by_name
from .extensions import db, migrate, mail, sess, csrf, redis_client
from .errors import register_error_handlers


def create_app(config_name: str | None = None) -> Flask:
    """Application factory.

    Args:
        config_name: One of 'development', 'production', 'testing'.
                     Defaults to FLASK_ENV env var or 'development'.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # ── Redis client ─────────────────────────────────────────────
    import app.extensions as ext
    ext.redis_client = redis_lib.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        decode_responses=True,
    )
    app.config['SESSION_REDIS'] = redis_lib.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
    )

    # ── Extensions ───────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    sess.init_app(app)
    csrf.init_app(app)

    # ── Blueprints ───────────────────────────────────────────────
    from .auth.routes import auth_bp
    from .members.routes import members_bp
    from .subscriptions.routes import subscriptions_bp
    from .training.routes import training_bp
    from .billing.routes import billing_bp
    from .reports.routes import reports_bp
    from .settings.routes import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # ── Error handlers ───────────────────────────────────────────
    register_error_handlers(app)

    # ── Index route ──────────────────────────────────────────────
    @app.route('/')
    def index():
        from flask import redirect, url_for, session
        if 'user_id' in session:
            return redirect(url_for('auth.dashboard'))
        return redirect(url_for('auth.login'))

    return app
