from flask import Blueprint, request, jsonify
from models import db, LiquorLicense, LicenseStatus, LicenseType
from datetime import datetime, date, timedelta
import re
import secrets

license_bp = Blueprint('license', __name__)

def generate_license_number(license_type):
    """Generate a unique license number"""
    prefix = {
        LicenseType.RETAIL: 'RT',
        LicenseType.WHOLESALE: 'WH', 
        LicenseType.MANUFACTURER: 'MF',
        LicenseType.DISTRIBUTOR: 'DS',
        LicenseType.RESTAURANT: 'RS',
        LicenseType.BAR: 'BR'
    }.get(license_type, 'GN')
    
    year = str(date.today().year)[-2:]
    random_part = secrets.token_hex(4).upper()
    return f"{prefix}{year}{random_part}"

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Basic phone validation"""
    pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
    return re.match(pattern, phone) is not None

@license_bp.route('/licenses', methods=['GET'])
def get_licenses():
    """Get all licenses with optional filtering"""
    status = request.args.get('status')
    license_type = request.args.get('type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = LiquorLicense.query
    
    if status:
        try:
            status_enum = LicenseStatus(status)
            query = query.filter(LiquorLicense.status == status_enum)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
    
    if license_type:
        try:
            type_enum = LicenseType(license_type)
            query = query.filter(LiquorLicense.license_type == type_enum)
        except ValueError:
            return jsonify({'error': 'Invalid license type'}), 400
    
    licenses = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'licenses': [license.to_dict() for license in licenses.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': licenses.total,
            'pages': licenses.pages,
            'has_prev': licenses.has_prev,
            'has_next': licenses.has_next
        }
    })

@license_bp.route('/licenses/<license_number>', methods=['GET'])
def get_license(license_number):
    """Get a specific license by license number"""
    license = LiquorLicense.query.filter_by(license_number=license_number).first()
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    return jsonify(license.to_dict())

@license_bp.route('/licenses', methods=['POST'])
def create_license():
    """Create a new liquor license"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields validation
    required_fields = [
        'license_type', 'business_name', 'owner_name', 'owner_email', 
        'owner_phone', 'address_line1', 'city', 'state', 'zip_code'
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate license type
    try:
        license_type = LicenseType(data['license_type'])
    except ValueError:
        valid_types = [lt.value for lt in LicenseType]
        return jsonify({'error': f'Invalid license type. Valid types: {valid_types}'}), 400
    
    # Validate email and phone
    if not validate_email(data['owner_email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_phone(data['owner_phone']):
        return jsonify({'error': 'Invalid phone format'}), 400
    
    # Generate unique license number
    license_number = generate_license_number(license_type)
    while LiquorLicense.query.filter_by(license_number=license_number).first():
        license_number = generate_license_number(license_type)
    
    # Set expiration date (default 1 year from now)
    issue_date = date.today()
    expiration_date = issue_date + timedelta(days=365)
    
    # Create new license
    license = LiquorLicense(
        license_number=license_number,
        license_type=license_type,
        status=LicenseStatus.PENDING,
        business_name=data['business_name'],
        owner_name=data['owner_name'],
        owner_email=data['owner_email'],
        owner_phone=data['owner_phone'],
        address_line1=data['address_line1'],
        address_line2=data.get('address_line2'),
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        issue_date=issue_date,
        expiration_date=expiration_date,
        notes=data.get('notes')
    )
    
    try:
        db.session.add(license)
        db.session.commit()
        return jsonify(license.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create license'}), 500

@license_bp.route('/licenses/<license_number>/status', methods=['PUT'])
def update_license_status(license_number):
    """Update license status"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    license = LiquorLicense.query.filter_by(license_number=license_number).first()
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    try:
        new_status = LicenseStatus(data['status'])
    except ValueError:
        valid_statuses = [ls.value for ls in LicenseStatus]
        return jsonify({'error': f'Invalid status. Valid statuses: {valid_statuses}'}), 400
    
    license.status = new_status
    if data.get('notes'):
        license.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify(license.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update license status'}), 500

@license_bp.route('/licenses/<license_number>/renew', methods=['POST'])
def renew_license(license_number):
    """Renew a license (extend expiration date)"""
    data = request.get_json() or {}
    
    license = LiquorLicense.query.filter_by(license_number=license_number).first()
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    if license.status == LicenseStatus.REVOKED:
        return jsonify({'error': 'Cannot renew revoked license'}), 400
    
    # Default renewal period is 1 year
    renewal_days = data.get('renewal_days', 365)
    
    # Set new expiration date from current expiration or today, whichever is later
    base_date = max(license.expiration_date, date.today())
    license.expiration_date = base_date + timedelta(days=renewal_days)
    
    # Update status to active if it was expired
    if license.status == LicenseStatus.EXPIRED:
        license.status = LicenseStatus.ACTIVE
    
    try:
        db.session.commit()
        return jsonify(license.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to renew license'}), 500

@license_bp.route('/licenses/<license_number>/validate', methods=['GET'])
def validate_license(license_number):
    """Validate if a license is currently valid"""
    
    license = LiquorLicense.query.filter_by(license_number=license_number).first()
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    is_valid = (
        license.status == LicenseStatus.ACTIVE and 
        not license.is_expired
    )
    
    validation_result = {
        'license_number': license_number,
        'is_valid': is_valid,
        'status': license.status.value,
        'is_expired': license.is_expired,
        'expiration_date': license.expiration_date.isoformat(),
        'days_until_expiration': license.days_until_expiration,
        'business_name': license.business_name
    }
    
    if not is_valid:
        reasons = []
        if license.status != LicenseStatus.ACTIVE:
            reasons.append(f"Status is {license.status.value}")
        if license.is_expired:
            reasons.append("License has expired")
        validation_result['invalid_reasons'] = reasons
    
    return jsonify(validation_result)

@license_bp.route('/licenses/search', methods=['GET'])
def search_licenses():
    """Search licenses by business name or owner name"""
    query_param = request.args.get('q', '').strip()
    if not query_param:
        return jsonify({'error': 'Search query is required'}), 400
    
    licenses = LiquorLicense.query.filter(
        db.or_(
            LiquorLicense.business_name.ilike(f'%{query_param}%'),
            LiquorLicense.owner_name.ilike(f'%{query_param}%')
        )
    ).limit(20).all()
    
    return jsonify({
        'query': query_param,
        'results': [license.to_dict() for license in licenses],
        'count': len(licenses)
    })