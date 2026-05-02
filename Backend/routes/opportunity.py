from datetime import datetime

from flask import Blueprint, request, jsonify, session

from extensions import db
from models import Admin, Opportunity
from utils.validators import validate_opportunity

opportunity_bp = Blueprint('opportunity', __name__, url_prefix='/api/opportunities')


# ── Auth helper (local to avoid circular import) ──────────────────────────────

def _get_current_admin():
    admin_id = session.get('admin_id')
    return Admin.query.get(admin_id) if admin_id else None


def _login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _get_current_admin():
            return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated


# ── US-2.1  View All Opportunities ───────────────────────────────────────────

@opportunity_bp.route('', methods=['GET'])
@_login_required
def get_opportunities():
    admin = _get_current_admin()
    opps  = (
        Opportunity.query
        .filter_by(admin_id=admin.id)
        .order_by(Opportunity.created_at.desc())
        .all()
    )
    return jsonify([o.to_dict() for o in opps]), 200


# ── US-2.2  Add a New Opportunity ────────────────────────────────────────────

@opportunity_bp.route('', methods=['POST'])
@_login_required
def create_opportunity():
    admin           = _get_current_admin()
    data            = request.get_json() or {}
    cleaned, errors = validate_opportunity(data)

    if errors:
        return jsonify({'errors': errors}), 400

    opp = Opportunity(
        admin_id             = admin.id,
        name                 = cleaned['name'],
        duration             = cleaned['duration'],
        start_date           = cleaned['start_date'],
        description          = cleaned['description'],
        skills               = cleaned['skills'],
        category             = cleaned['category'],
        future_opportunities = cleaned['future_opportunities'],
        max_applicants       = cleaned['max_applicants'],
    )
    db.session.add(opp)
    db.session.commit()

    return jsonify(opp.to_dict()), 201


# ── US-2.4  View Opportunity Details ─────────────────────────────────────────

@opportunity_bp.route('/<int:opp_id>', methods=['GET'])
@_login_required
def get_opportunity(opp_id):
    admin = _get_current_admin()
    opp   = Opportunity.query.filter_by(id=opp_id, admin_id=admin.id).first()
    if not opp:
        return jsonify({'error': 'Opportunity not found.'}), 404
    return jsonify(opp.to_dict()), 200


# ── US-2.5  Edit an Opportunity ───────────────────────────────────────────────

@opportunity_bp.route('/<int:opp_id>', methods=['PUT'])
@_login_required
def update_opportunity(opp_id):
    admin = _get_current_admin()
    opp   = Opportunity.query.filter_by(id=opp_id, admin_id=admin.id).first()
    if not opp:
        return jsonify({'error': 'Opportunity not found.'}), 404

    data            = request.get_json() or {}
    cleaned, errors = validate_opportunity(data)
    if errors:
        return jsonify({'errors': errors}), 400

    opp.name                 = cleaned['name']
    opp.duration             = cleaned['duration']
    opp.start_date           = cleaned['start_date']
    opp.description          = cleaned['description']
    opp.skills               = cleaned['skills']
    opp.category             = cleaned['category']
    opp.future_opportunities = cleaned['future_opportunities']
    opp.max_applicants       = cleaned['max_applicants']
    opp.updated_at           = datetime.utcnow()
    db.session.commit()

    return jsonify(opp.to_dict()), 200


# ── US-2.6  Delete an Opportunity ────────────────────────────────────────────

@opportunity_bp.route('/<int:opp_id>', methods=['DELETE'])
@_login_required
def delete_opportunity(opp_id):
    admin = _get_current_admin()
    opp   = Opportunity.query.filter_by(id=opp_id, admin_id=admin.id).first()
    if not opp:
        return jsonify({'error': 'Opportunity not found.'}), 404

    db.session.delete(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted successfully.'}), 200
