from flask import Flask
from config import Config
from models import db, User, Role
from routes import bp as api_bp
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# Load configuration
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with db.session() as session:
        return session.get(User, int(user_id))

# Register Blueprints
app.register_blueprint(api_bp, url_prefix='/api')

def init_roles():
    roles = ['user', 'employee', 'admin', 'customer']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
            db.session.commit()
            print(f"Role '{role_name}' created.")
        else:
            print(f"Role '{role_name}' already exists.")

with app.app_context():
    db.create_all()
    init_roles()

if not app.debug:
    handler = RotatingFileHandler(
        app.config['LOGGING_LOCATION'],
        maxBytes=app.config['LOGGING_MAX_BYTES'],
        backupCount=app.config['LOGGING_BACKUP_COUNT']
    )
    handler.setLevel(app.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

if __name__ == '__main__':
    app.run(debug=True)

