from flask import jsonify
import logging

log = logging.getLogger("security")


class ApiError(Exception):
    def __init__(self, message="Bad Request", status_code=400, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def register_error_handlers(app):

    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return jsonify({
            "error": err.message,
            "details": err.details
        }), err.status_code

    @app.errorhandler(400)
    def bad_request(_):
        return jsonify({"error": "Bad Request"}), 400

    @app.errorhandler(401)
    def unauthorized(_):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(_):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method Not Allowed"}), 405

    @app.errorhandler(500)
    def internal_error(_):
        return jsonify({"error": "Internal Server Error"}), 500
