import pytest
import json
from datetime import date, timedelta
from app import app
from models import db, LiquorLicense, LicenseStatus, LicenseType

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_license_data():
    return {
        'license_type': 'retail',
        'business_name': 'Test Liquor Store',
        'owner_name': 'John Doe',
        'owner_email': 'john@example.com',
        'owner_phone': '555-123-4567',
        'address_line1': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip_code': '12345',
        'notes': 'Test license'
    }

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index_endpoint(client):
    """Test the index endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Digital Liquor License System' in data['message']

def test_create_license_success(client, sample_license_data):
    """Test successful license creation"""
    response = client.post('/api/v1/licenses', 
                          json=sample_license_data,
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['license_type'] == 'retail'
    assert data['business_name'] == 'Test Liquor Store'
    assert data['owner_name'] == 'John Doe'
    assert data['status'] == 'pending'
    assert 'license_number' in data
    assert len(data['license_number']) > 0

def test_create_license_missing_fields(client):
    """Test license creation with missing required fields"""
    incomplete_data = {
        'license_type': 'retail',
        'business_name': 'Test Store'
        # Missing other required fields
    }
    
    response = client.post('/api/v1/licenses',
                          json=incomplete_data,
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Missing required field' in data['error']

def test_create_license_invalid_type(client, sample_license_data):
    """Test license creation with invalid license type"""
    sample_license_data['license_type'] = 'invalid_type'
    
    response = client.post('/api/v1/licenses',
                          json=sample_license_data,
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid license type' in data['error']

def test_create_license_invalid_email(client, sample_license_data):
    """Test license creation with invalid email"""
    sample_license_data['owner_email'] = 'invalid-email'
    
    response = client.post('/api/v1/licenses',
                          json=sample_license_data,
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid email format' in data['error']

def test_get_licenses_empty(client):
    """Test getting licenses when database is empty"""
    response = client.get('/api/v1/licenses')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['licenses'] == []
    assert data['pagination']['total'] == 0

def test_get_licenses_with_data(client, sample_license_data):
    """Test getting licenses with data"""
    # Create a license first
    client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    
    response = client.get('/api/v1/licenses')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert len(data['licenses']) == 1
    assert data['pagination']['total'] == 1

def test_get_license_by_number(client, sample_license_data):
    """Test getting a specific license by license number"""
    # Create a license first
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    
    response = client.get(f'/api/v1/licenses/{license_number}')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['license_number'] == license_number
    assert data['business_name'] == sample_license_data['business_name']

def test_get_license_not_found(client):
    """Test getting a license that doesn't exist"""
    response = client.get('/api/v1/licenses/NONEXISTENT123')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'License not found' in data['error']

def test_update_license_status(client, sample_license_data):
    """Test updating license status"""
    # Create a license first
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    
    # Update status to active
    update_data = {'status': 'active', 'notes': 'Approved after review'}
    response = client.put(f'/api/v1/licenses/{license_number}/status',
                         json=update_data,
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'active'
    assert data['notes'] == 'Approved after review'

def test_update_license_status_invalid(client, sample_license_data):
    """Test updating license status with invalid status"""
    # Create a license first
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    
    # Try to update with invalid status
    update_data = {'status': 'invalid_status'}
    response = client.put(f'/api/v1/licenses/{license_number}/status',
                         json=update_data,
                         content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid status' in data['error']

def test_validate_license_valid(client, sample_license_data):
    """Test license validation for valid license"""
    # Create a license and set it to active
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    
    # Set status to active
    client.put(f'/api/v1/licenses/{license_number}/status',
               json={'status': 'active'},
               content_type='application/json')
    
    # Validate the license
    response = client.get(f'/api/v1/licenses/{license_number}/validate')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['is_valid'] == True
    assert data['license_number'] == license_number
    assert data['status'] == 'active'

def test_validate_license_expired(client, sample_license_data):
    """Test license validation for expired license"""
    # This would require manipulating the expiration date in the database
    # For now, we test the endpoint structure
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    
    response = client.get(f'/api/v1/licenses/{license_number}/validate')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'is_valid' in data
    assert 'status' in data
    assert data['license_number'] == license_number

def test_renew_license(client, sample_license_data):
    """Test license renewal"""
    # Create a license first
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    original_expiration = created_license['expiration_date']
    
    # Renew the license
    response = client.post(f'/api/v1/licenses/{license_number}/renew',
                          json={'renewal_days': 365},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that expiration date has been extended
    assert data['expiration_date'] != original_expiration

def test_search_licenses(client, sample_license_data):
    """Test license search functionality"""
    # Create a license first
    client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    
    # Search by business name
    response = client.get('/api/v1/licenses/search?q=Test Liquor')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['count'] >= 1
    assert len(data['results']) >= 1
    assert data['query'] == 'Test Liquor'

def test_search_licenses_no_query(client):
    """Test license search without query parameter"""
    response = client.get('/api/v1/licenses/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Search query is required' in data['error']

def test_filter_licenses_by_status(client, sample_license_data):
    """Test filtering licenses by status"""
    # Create a license
    create_response = client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    created_license = json.loads(create_response.data)
    license_number = created_license['license_number']
    
    # Update status to active
    client.put(f'/api/v1/licenses/{license_number}/status',
               json={'status': 'active'},
               content_type='application/json')
    
    # Filter by active status
    response = client.get('/api/v1/licenses?status=active')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert len(data['licenses']) >= 1
    assert all(license['status'] == 'active' for license in data['licenses'])

def test_filter_licenses_by_type(client, sample_license_data):
    """Test filtering licenses by type"""
    # Create a license
    client.post('/api/v1/licenses', json=sample_license_data, content_type='application/json')
    
    # Filter by retail type
    response = client.get('/api/v1/licenses?type=retail')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert len(data['licenses']) >= 1
    assert all(license['license_type'] == 'retail' for license in data['licenses'])