from flask import Flask, jsonify, request
from dotenv import load_dotenv
import logging

from .config import Config
from .extensions import db, migrate, jwt, limiter
from .auth.routes import bp as auth_bp
from .notes.routes import bp as notes_bp
from .errors import register_error_handlers
from .security_headers import apply_security_headers
from .auth.service import is_jti_revoked


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    # -------------------
    # JWT SECURITY HOOKS
    # -------------------

    @jwt.token_in_blocklist_loader
    def check_if_revoked(jwt_header, jwt_payload):
        return is_jti_revoked(jwt_payload.get("jti"))

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        logging.getLogger("security").info(
            "Unauthorized access ip=%s path=%s reason=%s",
            request.remote_addr,
            request.path,
            reason
        )
        return {"error": "Unauthorized"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        logging.getLogger("security").info(
            "Invalid token ip=%s path=%s reason=%s",
            request.remote_addr,
            request.path,
            reason
        )
        return {"error": "Unauthorized"}, 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logging.getLogger("security").info(
            "Expired token ip=%s path=%s",
            request.remote_addr,
            request.path
        )
        return {"error": "Token expired"}, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        logging.getLogger("security").info(
            "Revoked token used ip=%s path=%s",
            request.remote_addr,
            request.path
        )
        return {"error": "Token revoked"}, 401

    # -------------------
    # BLUEPRINTS
    # -------------------

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(notes_bp, url_prefix="/notes")

    # -------------------
    # BASIC ROUTES
    # -------------------

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # -------------------
    # SECURITY + ERRORS
    # -------------------

    apply_security_headers(app)
    register_error_handlers(app)

    return app
