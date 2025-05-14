# This script is used to run the Flask application.
from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=9999, debug=True)