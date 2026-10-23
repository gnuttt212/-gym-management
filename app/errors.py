"""Global error handlers returning consistent JSON responses."""

from flask import jsonify, render_template, request


def _wants_json() -> bool:
    """Check if the client prefers JSON over HTML."""
    return (
        request.accept_mimetypes.best == 'application/json'
        or request.path.endswith('.json')
    )


def register_error_handlers(app):
    """Register error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(e):
        if _wants_json():
            return jsonify(error={'code': 'BAD_REQUEST', 'message': str(e)}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if _wants_json():
            return jsonify(error={'code': 'UNAUTHORIZED', 'message': 'Authentication required.'}), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        if _wants_json():
            return jsonify(error={'code': 'FORBIDDEN', 'message': 'You do not have permission.'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        if _wants_json():
            return jsonify(error={'code': 'NOT_FOUND', 'message': 'Resource not found.'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        if _wants_json():
            return jsonify(error={'code': 'INTERNAL_ERROR', 'message': 'An unexpected error occurred.'}), 500
        return render_template('errors/500.html'), 500
