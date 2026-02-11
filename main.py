import os
import subprocess

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from app.routes import api

load_dotenv()

# Run database migrations on startup
try:
    subprocess.run(["alembic", "upgrade", "head"], check=True, capture_output=True)
    print("Database migrations applied successfully")
except subprocess.CalledProcessError as e:
    print(f"Warning: Migration failed: {e.stderr.decode()}")

app = Flask(__name__)

# Register blueprints
app.register_blueprint(api)

if os.getenv("DEBUG"):
    CORS(
        app,
        origins=["http://localhost:5173"],
        methods=["GET", "POST", "PUT", "DELETE"],
    )

# SENTRY
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment="production",
    )


# ERRORS
@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "The requested URL was not found on the server."}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"detail": "An unexpected error occurred."}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error(f"Unhandled exception: {error}", exc_info=True)

    return jsonify({"detail": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
