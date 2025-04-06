from flask import Flask, request, jsonify, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import redirect, url_for
import re
import logging
import os
app = Flask(__name__)

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

# Environment Configuration
DEBUG = os.getenv("DEBUG", "False") == "True"

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return Admin()  # Return an Admin object
    return User.query.get(int(user_id))  # Handle regular users


# Valid BioIDs (from coursework)
VALID_BIO_IDS = [
    "K1YL8VA2HG", "7DMPYAZAP2", "D05HPPQNJ4", "2WYIM3QCK9", "DHKFIYHMAZ",
    "LZK7P0X0LQ", "H5C98XCENC", "6X6I6TSUFG", "QTLCWUS8NB", "Y4FC3F9ZGS",
    "V30EPKZQI2", "O3WJFGR5WE", "SEIQTS1H16", "X16V7LFHR2", "TLFDFY7RDG",
    "PGPVG5RF42", "FPALKDEL5T", "2BIB99Z54V", "ABQYUQCQS2", "9JSXWO4LGH",
    "QJXQOUPTH9", "GOYWJVDA8A", "6EBQ28A62V", "30MY51J1CJ", "FH6260T08H",
    "JHDCXB62SA", "O0V55ENOT0", "F3ATSRR5DQ", "1K3JTWHA05", "FINNMWJY0G",
    "CET8NUAE09", "VQKBGSE3EA", "E7D6YUPQ6J", "BPX8O0YB5L", "AT66BX2FXM",
    "1PUQV970LA", "CCU1D7QXDT", "TTK74SYYAN", "4HTOAI9YKO", "PD6XPNB80J",
    "BZW5WWDMUY", "340B1EOCMG", "CG1I9SABLL", "49YFTUA96K", "V2JX0IC633",
    "C7IFP4VWIL", "RYU8VSS4N5", "S22A588D75", "88V3GKIVSF", "8OLYIE2FRC"
]

# Admin Credentials
ADMIN_EMAIL = "admin@petition.parliament.sr"
ADMIN_PASSWORD = "2025%shangrila"
SIGNATURE_THRESHOLD = 100

# Admin Class
class Admin:
    """
    Represents the admin user for the Petitions Committee.
    """
    def __init__(self):
        self.id = "admin"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    bio_id = db.Column(db.String(10), unique=True, nullable=False)

    @property
    def is_active(self):
        return True

# Petition Model
class Petition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), default="open")
    petitioner_email = db.Column(db.String(150), db.ForeignKey('user.email'), nullable=False)
    signatures = db.Column(db.Integer, default=0)
    response = db.Column(db.Text, default="")

class PetitionSignature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    petition_id = db.Column(db.Integer, db.ForeignKey('petition.id'), nullable=False)
    signer_email = db.Column(db.String(150), db.ForeignKey('user.email'), nullable=False)

with app.app_context():
    db.create_all()

# Validation Functions
def validate_registration_input(data):
    if not data.get("email") or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        abort(400, description="Invalid email format.")
    if not data.get("name") or len(data["name"]) < 3:
        abort(400, description="Name must be at least 3 characters.")
    if not data.get("password") or len(data["password"]) < 8:
        abort(400, description="Password must be at least 8 characters.")

def validate_petition_input(data):
    if not data.get("title") or len(data["title"]) < 5:
        abort(400, description="Petition title must be at least 5 characters.")
    if not data.get("content") or len(data["content"]) < 20:
        abort(400, description="Petition content must be at least 20 characters.")

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Registration Page Route
@app.route('/register')
def register_page():
    return render_template('register.html')

# Login Page Route
@app.route('/login')
def login_page():
    return render_template('login.html')

# Petitioner Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Registration Route
@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    validate_registration_input(data)
    
    # Check if the BioID is valid
    if data['bio_id'] not in VALID_BIO_IDS:
        return jsonify({"error": "Invalid BioID. Please enter a valid BioID from the provided list."}), 400

    # Check if the BioID is already associated with a user
    existing_user = User.query.filter_by(bio_id=data['bio_id']).first()
    if existing_user:
        return jsonify({"error": "This BioID is already associated with another user."}), 400

    # Proceed with user registration
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        email=data['email'],
        name=data['name'],
        dob=data['dob'],
        password=hashed_password,
        bio_id=data['bio_id']
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({"error": "An unexpected error occurred during registration."}), 500

# Login Route
@app.route('/login', methods=['POST'])
def petitioner_login():
    """
    Handles petitioner login.
    """
    data = request.json
    user = User.query.filter_by(email=data['email']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials."}), 401

    login_user(user)
    return jsonify({"message": f"Welcome back, {user.name}!"}), 200


@app.route('/admin/login', methods=['POST'], endpoint='admin_login_route')
def admin_login():
    """
    Handles admin login.
    """
    ADMIN_EMAIL = "admin@petition.parliament.sr"
    ADMIN_PASSWORD = "2025%shangrila"
    data = request.json
    if data['email'] == ADMIN_EMAIL and data['password'] == ADMIN_PASSWORD:
        admin_user = Admin()
        login_user(admin_user)
        return jsonify({"message": "Admin logged in successfully!"}), 200
    else:
        return jsonify({"error": "Invalid admin credentials"}), 401


# Logout Route

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))  # Redirect to the home page
  
# Create Petition Route
@app.route('/create_petition', methods=['POST'])
@login_required
def create_petition():
    data = request.json

    # Validate the petition input
    validate_petition_input(data)

    # Check if a petition with the same title and content already exists
    existing_petition = Petition.query.filter_by(title=data['title'], content=data['content']).first()
    if existing_petition:
        return jsonify({"error": "A petition with the same title and content already exists."}), 400

    # Proceed to create a new petition
    new_petition = Petition(
        title=data['title'],
        content=data['content'],
        petitioner_email=current_user.email  # Associate the petition with the logged-in user's email
    )
    try:
        db.session.add(new_petition)
        db.session.commit()
        return jsonify({"message": "Petition created successfully!"}), 201
    except Exception as e:
        logger.error(f"Error creating petition: {e}")
        return jsonify({"error": "An unexpected error occurred while creating the petition."}), 500

# View Petitions Route
@app.route('/petitions', methods=['GET'])
@login_required
def view_petitions():
    petitions = Petition.query.all()
    petitions_list = [
        {
            "id": petition.id,
            "title": petition.title,
            "content": petition.content,
            "status": petition.status,
            "signatures": petition.signatures,
            "response": petition.response,
            "petitioner_email": petition.petitioner_email
        }
        for petition in petitions
    ]
    return jsonify({"petitions": petitions_list}), 200

# Sign Petition Route

@app.route('/sign_petition/<int:petition_id>', methods=['POST'])
@login_required
def sign_petition(petition_id):
    petition = Petition.query.get(petition_id)
    if not petition:
        return jsonify({"error": "Petition not found."}), 404
    if petition.status != "open":
        return jsonify({"error": "This petition is closed."}), 400
    if petition.petitioner_email == current_user.email:
        return jsonify({"error": "You cannot sign your own petition."}), 400
    if PetitionSignature.query.filter_by(petition_id=petition_id, signer_email=current_user.email).first():
        return jsonify({"error": "You have already signed this petition."}), 400

    new_signature = PetitionSignature(petition_id=petition_id, signer_email=current_user.email)
    petition.signatures += 1
    db.session.add(new_signature)
    db.session.commit()
    return jsonify({"message": "Petition signed successfully!"}), 200

# Admin Login Route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required."}), 400

    if data['email'] == ADMIN_EMAIL and data['password'] == ADMIN_PASSWORD:
        admin_user = Admin()
        login_user(admin_user)
        return jsonify({"message": "Admin logged in successfully!"}), 200

    return jsonify({"error": "Invalid admin credentials"}), 401

# Admin Dashboard Route
@app.route('/admin/dashboard', methods=['GET'], endpoint='admin_dashboard_route')
@login_required
def admin_dashboard():
    """
    Admin Dashboard: Displays all petitions and their details.
    """
    if not isinstance(current_user, Admin):
        return jsonify({"error": "Unauthorized access. Admins only."}), 403

    petitions = Petition.query.all()
    petitions_list = [
        {
            "id": petition.id,
            "title": petition.title,
            "content": petition.content,
            "status": petition.status,
            "signatures": petition.signatures,
            "response": petition.response,
        }
        for petition in petitions
    ]
    return render_template('admin_dashboard.html', petitions=petitions_list)



# Admin Set Threshold API
@app.route('/admin/set_threshold', methods=['POST'])
@login_required
def set_threshold():
    if not isinstance(current_user, Admin):
        return jsonify({"error": "Unauthorized access. Admins only."}), 403

    data = request.json
    try:
        global SIGNATURE_THRESHOLD
        SIGNATURE_THRESHOLD = int(data['threshold'])
        return jsonify({"message": f"Signature threshold set to {SIGNATURE_THRESHOLD}!"}), 200
    except ValueError:
        return jsonify({"error": "Invalid threshold value"}), 400


# Admin View All Petitions API
@app.route('/admin/view_petitions', methods=['GET'])
@login_required
def admin_view_petitions():
    global SIGNATURE_THRESHOLD
    petitions = Petition.query.all()
    petitions_list = [
        {
            "id": petition.id,
            "title": petition.title,
            "content": petition.content,
            "status": petition.status,
            "signatures": petition.signatures,
            "response": petition.response or "No response yet",
        }
        for petition in petitions
    ]
    return jsonify({"petitions": petitions_list, "threshold": SIGNATURE_THRESHOLD}), 200


# Admin Close Petition API
@app.route('/admin/respond_petition/<int:petition_id>', methods=['POST'])
@login_required
def respond_petition(petition_id):
    data = request.json
    petition = Petition.query.get(petition_id)

    if not petition or petition.status != "open":
        return jsonify({"error": "Petition is not open for response"}), 400

    petition.response = data.get("response", "").strip()
    if not petition.response:
        return jsonify({"error": "Response cannot be empty"}), 400

    petition.status = "closed"  # Update status

    try:
        db.session.commit()
        return jsonify({"message": f"Petition {petition_id} has been responded to and closed successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update petition status: {str(e)}"}), 500

# Open Data REST API: List all petitions
# Open Data REST API: List all petitions with optional filtering
@app.route('/slpp/petitions', methods=['GET'])
def api_list_petitions():
    # Get the 'status' query parameter from the request
    status = request.args.get('status')

    if status:  # If 'status' is provided, filter petitions
        petitions = Petition.query.filter_by(status=status).all()
    else:  # Otherwise, return all petitions
        petitions = Petition.query.all()

    petitions_list = [
        {
            "id": petition.id,
            "title": petition.title,
            "content": petition.content,
            "status": petition.status,
            "signatures": petition.signatures,
            "response": petition.response or "No response yet",
            "petitioner_email": petition.petitioner_email
        }
        for petition in petitions
    ]
    return jsonify({"petitions": petitions_list}), 200


# Open Data REST API: Get petition details
@app.route('/api/petitions/<int:petition_id>', methods=['GET'])
def api_get_petition(petition_id):
    petition = Petition.query.get(petition_id)
    if not petition:
        return jsonify({"error": "Petition not found."}), 404

    petition_details = {
        "id": petition.id,
        "title": petition.title,
        "content": petition.content,
        "status": petition.status,
        "signatures": petition.signatures,
        "response": petition.response or "No response yet",
        "petitioner_email": petition.petitioner_email
    }
    return jsonify({"petition": petition_details}), 200

# Open Data REST API: Get petition signatures
@app.route('/api/petitions/<int:petition_id>/signatures', methods=['GET'])
def api_get_petition_signatures(petition_id):
    signatures = PetitionSignature.query.filter_by(petition_id=petition_id).all()
    if not signatures:
        return jsonify({"error": "No signatures found for this petition."}), 404

    signatures_list = [{"signer_email": signature.signer_email} for signature in signatures]
    return jsonify({"signatures": signatures_list}), 200


# Error Handlers
@app.errorhandler(403)
def forbidden_error(e):
    return jsonify({"error": "Forbidden access."}), 403

@app.errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "The requested resource was not found."}), 404

@app.errorhandler(500)
def internal_error(e):
    if DEBUG:
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500
    return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)