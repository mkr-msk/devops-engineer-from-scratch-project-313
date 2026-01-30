from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ping')
def ping():
  return 'pong'

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