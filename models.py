from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from enum import Enum

# Import db from a separate module to avoid circular imports
db = SQLAlchemy()

class LicenseStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    PENDING = "pending"

class LicenseType(Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale" 
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    RESTAURANT = "restaurant"
    BAR = "bar"

class LiquorLicense(db.Model):
    __tablename__ = 'liquor_licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    license_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    license_type = db.Column(db.Enum(LicenseType), nullable=False)
    status = db.Column(db.Enum(LicenseStatus), nullable=False, default=LicenseStatus.PENDING)
    
    # License holder information
    business_name = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    owner_email = db.Column(db.String(100), nullable=False)
    owner_phone = db.Column(db.String(20), nullable=False)
    
    # Business address
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    
    # License dates
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    expiration_date = db.Column(db.Date, nullable=False)
    
    # Audit fields
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional fields for compliance
    notes = db.Column(db.Text)
    last_inspection_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<LiquorLicense {self.license_number}>'
    
    @property
    def is_expired(self):
        return date.today() > self.expiration_date
    
    @property
    def days_until_expiration(self):
        if self.is_expired:
            return 0
        return (self.expiration_date - date.today()).days
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_number': self.license_number,
            'license_type': self.license_type.value,
            'status': self.status.value,
            'business_name': self.business_name,
            'owner_name': self.owner_name,
            'owner_email': self.owner_email,
            'owner_phone': self.owner_phone,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code
            },
            'issue_date': self.issue_date.isoformat(),
            'expiration_date': self.expiration_date.isoformat(),
            'is_expired': self.is_expired,
            'days_until_expiration': self.days_until_expiration,
            'notes': self.notes,
            'last_inspection_date': self.last_inspection_date.isoformat() if self.last_inspection_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }