from flask import Flask
from flask.logging import create_logger
import logging

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger = create_logger(app)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    app.logger.info("999Security Diagnostics - Educational Security Testing Platform Initialized")
    return app