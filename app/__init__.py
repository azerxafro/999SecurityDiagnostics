from flask import Flask
from flask.logging import create_logger
from flask_socketio import SocketIO
import logging

socketio = SocketIO()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger = create_logger(app)
    
    # Initialize SocketIO with the app
    socketio.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    app.logger.info("999Security Diagnostics - Educational Security Testing Platform Initialized")
    return app