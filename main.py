import os

import sentry_sdk
from flask import Flask, jsonify
from sentry_sdk.integrations.flask import FlaskIntegration

app = Flask(__name__)

# SENTRY
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
  sentry_sdk.init(
    dsn=sentry_dsn,
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment="production",
  )

# HEALTH CHECK
@app.route('/ping')
def ping():
  1/0
  return 'pong'

# ERRORS
@app.errorhandler(404)
def not_found(error):
  return jsonify({
    'error': 'Not Found',
    'message': 'The requested URL was not found on the server.'
  }), 404

@app.errorhandler(500)
def internal_error(error):
  return jsonify({
    'error': 'Internal Server Error',
    'message': 'An unexpected error occurred.'
  }), 500

@app.errorhandler(Exception)
def handle_exception(error):
  app.logger.error(f'Unhandled exception: {error}', exc_info=True)
  
  return jsonify({
    'error': 'Internal Server Error',
    'message': 'An unexpected error occurred.'
  }), 500


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)