# This script is used to run the Flask application.
from app import create_app

app = create_app()

# Vercel Python entrypoint
# Expose 'app' as the entrypoint for Vercel
# (Vercel will look for 'app' in run.py)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=True)