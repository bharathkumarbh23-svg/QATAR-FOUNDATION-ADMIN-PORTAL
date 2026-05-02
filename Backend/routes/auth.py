from flask import Blueprint, request, jsonify, session

from extensions import db, bcrypt
from models import Admin
from utils.validators import validate_signup
from utils.token import generate_reset_token, log_reset_link, consume_reset_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_current_admin():
    admin_id = session.get('admin_id')
    return Admin.query.get(admin_id) if admin_id else None


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_admin():
            return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated


# ── US-1.1  Sign Up ───────────────────────────────────────────────────────────

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data   = request.get_json() or {}
    errors = validate_signup(data)
    if errors:
        return jsonify({'errors': errors}), 400

    email = data['email'].strip().lower()

    if Admin.query.filter_by(email=email).first():
        return jsonify({'errors': {'email': 'An account with this email already exists.'}}), 409

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    admin     = Admin(
        full_name     = data['full_name'].strip(),
        email         = email,
        password_hash = hashed_pw,
    )
    db.session.add(admin)
    db.session.commit()

    return jsonify({'message': 'Account created successfully. Please log in.'}), 201


# ── US-1.2  Login ─────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
def login():
    data        = request.get_json() or {}
    email       = (data.get('email') or '').strip().lower()
    password    = data.get('password') or ''
    remember_me = bool(data.get('remember_me', False))

    admin = Admin.query.filter_by(email=email).first()

    # Generic error — do not reveal which field is wrong
    if not admin or not bcrypt.check_password_hash(admin.password_hash, password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    session.permanent = remember_me
    session['admin_id'] = admin.id

    return jsonify({
        'message': 'Login successful.',
        'admin': {
            'id':        admin.id,
            'full_name': admin.full_name,
            'email':     admin.email,
        }
    }), 200


# ── US-1.3  Forgot Password ───────────────────────────────────────────────────

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data  = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()

    # Always the same message — privacy protection
    GENERIC = 'If this email is registered, a reset link has been sent.'

    admin = Admin.query.filter_by(email=email).first()
    if admin:
        token = generate_reset_token(admin)
        log_reset_link(email, token)

    return jsonify({'message': GENERIC}), 200


# ── Reset Password (consumes token) ──────────────────────────────────────────

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data      = request.get_json() or {}
    raw_token = data.get('token') or ''
    password  = data.get('password') or ''

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters.'}), 400

    record, err = consume_reset_token(raw_token)
    if err:
        return jsonify({'error': err}), 400

    admin               = Admin.query.get(record.admin_id)
    admin.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    record.used         = True
    db.session.commit()

    return jsonify({'message': 'Password updated successfully. Please log in.'}), 200


# ── Logout ────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Signed out successfully.'}), 200


# ── Session info ──────────────────────────────────────────────────────────────

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    admin = get_current_admin()
    return jsonify({
        'id':        admin.id,
        'full_name': admin.full_name,
        'email':     admin.email,
    }), 200
