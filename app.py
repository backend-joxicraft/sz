from flask import Flask
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///liquor_licenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Import and initialize db
from models import db
db.init_app(app)

migrate = Migrate(app, db)

# Import models and routes after db initialization to avoid circular imports
from models import LiquorLicense
from routes import license_bp

app.register_blueprint(license_bp, url_prefix='/api/v1')

@app.route('/')
def index():
    return {'message': 'Digital Liquor License System', 'version': '1.0.0'}

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)