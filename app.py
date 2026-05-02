import os
from flask import Flask, render_template

from config import config
from extensions import db, bcrypt, cors
from routes.auth import auth_bp
from routes.opportunity import opportunity_bp


def create_app(env: str = None) -> Flask:
    """Application factory."""
    env = env or os.environ.get('FLASK_ENV', 'default')
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Load config
    app.config.from_object(config[env])

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(opportunity_bp)

    # Serve frontend
    @app.route('/')
    def index():
        return render_template('admin.html')

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
