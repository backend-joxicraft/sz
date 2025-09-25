# Digital Liquor License System (SZ)

A comprehensive REST API system for managing digital liquor licenses. This system allows for creating, managing, validating, and tracking liquor licenses with full CRUD operations and compliance features.

## Features

- **License Management**: Create, read, update, and delete liquor licenses
- **Multiple License Types**: Support for retail, wholesale, manufacturer, distributor, restaurant, and bar licenses
- **Status Tracking**: Track license status (pending, active, expired, suspended, revoked)
- **Validation**: Real-time license validation and expiration checking
- **Renewal System**: Automated license renewal with configurable periods
- **Search & Filter**: Search licenses by business/owner name, filter by status and type
- **Audit Trail**: Complete audit logging with creation and update timestamps
- **Compliance Features**: Inspection date tracking, notes, and regulatory compliance

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite (configurable for PostgreSQL/MySQL)
- **Testing**: pytest with Flask test client
- **Environment Management**: python-dotenv

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sz
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Running Tests

```bash
pytest test_app.py -v
```

## API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### Health Check
- **GET** `/health` - Check API health status
- **GET** `/` - Get system information

#### License Management

##### Create License
- **POST** `/licenses`
- **Content-Type**: `application/json`

**Request Body:**
```json
{
  "license_type": "retail",
  "business_name": "ABC Liquor Store",
  "owner_name": "John Smith",
  "owner_email": "john@abcliquor.com",
  "owner_phone": "555-123-4567",
  "address_line1": "123 Main Street",
  "address_line2": "Suite 100",
  "city": "Anytown",
  "state": "CA",
  "zip_code": "12345",
  "notes": "New retail location"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "license_number": "RT24A1B2C3D4",
  "license_type": "retail",
  "status": "pending",
  "business_name": "ABC Liquor Store",
  "owner_name": "John Smith",
  "owner_email": "john@abcliquor.com",
  "owner_phone": "555-123-4567",
  "address": {
    "line1": "123 Main Street",
    "line2": "Suite 100",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345"
  },
  "issue_date": "2024-09-25",
  "expiration_date": "2025-09-25",
  "is_expired": false,
  "days_until_expiration": 365,
  "notes": "New retail location",
  "last_inspection_date": null,
  "created_at": "2024-09-25T10:30:00.000000",
  "updated_at": "2024-09-25T10:30:00.000000"
}
```

##### Get All Licenses
- **GET** `/licenses`
- **Query Parameters:**
  - `status` - Filter by status (pending, active, expired, suspended, revoked)
  - `type` - Filter by license type (retail, wholesale, manufacturer, distributor, restaurant, bar)
  - `page` - Page number (default: 1)
  - `per_page` - Items per page (default: 10, max: 100)

**Response (200 OK):**
```json
{
  "licenses": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_prev": false,
    "has_next": true
  }
}
```

##### Get License by Number
- **GET** `/licenses/{license_number}`

##### Update License Status
- **PUT** `/licenses/{license_number}/status`

**Request Body:**
```json
{
  "status": "active",
  "notes": "Approved after inspection"
}
```

##### Validate License
- **GET** `/licenses/{license_number}/validate`

**Response (200 OK):**
```json
{
  "license_number": "RT24A1B2C3D4",
  "is_valid": true,
  "status": "active",
  "is_expired": false,
  "expiration_date": "2025-09-25",
  "days_until_expiration": 300,
  "business_name": "ABC Liquor Store"
}
```

##### Renew License
- **POST** `/licenses/{license_number}/renew`

**Request Body (Optional):**
```json
{
  "renewal_days": 365
}
```

##### Search Licenses
- **GET** `/licenses/search?q={search_term}`
- Searches business names and owner names

### License Types

- `retail` - Retail liquor stores
- `wholesale` - Wholesale distributors
- `manufacturer` - Liquor manufacturers
- `distributor` - Distribution companies
- `restaurant` - Restaurants serving alcohol
- `bar` - Bars and taverns

### License Status

- `pending` - Application submitted, awaiting approval
- `active` - License is active and valid
- `expired` - License has expired
- `suspended` - License temporarily suspended
- `revoked` - License permanently revoked

## Data Model

### LiquorLicense

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| license_number | String(50) | Unique license identifier |
| license_type | Enum | Type of license |
| status | Enum | Current license status |
| business_name | String(200) | Name of the business |
| owner_name | String(100) | Name of the license holder |
| owner_email | String(100) | Contact email |
| owner_phone | String(20) | Contact phone |
| address_line1 | String(200) | Business address line 1 |
| address_line2 | String(200) | Business address line 2 (optional) |
| city | String(100) | Business city |
| state | String(50) | Business state |
| zip_code | String(10) | Business ZIP code |
| issue_date | Date | Date license was issued |
| expiration_date | Date | Date license expires |
| notes | Text | Additional notes (optional) |
| last_inspection_date | Date | Last inspection date (optional) |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Record last update timestamp |

## Configuration

### Environment Variables

- `DATABASE_URL` - Database connection string (default: sqlite:///liquor_licenses.db)
- `SECRET_KEY` - Flask secret key for sessions
- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_DEBUG` - Enable debug mode (True/False)

### Database Configuration

The system uses SQLAlchemy and supports multiple databases:

- **SQLite** (default): `sqlite:///liquor_licenses.db`
- **PostgreSQL**: `postgresql://user:password@localhost/dbname`
- **MySQL**: `mysql://user:password@localhost/dbname`

## Testing

The system includes comprehensive tests covering:

- API endpoint functionality
- Data validation
- Error handling
- License lifecycle operations
- Search and filtering
- Status management
- License renewal

Run tests with:
```bash
pytest test_app.py -v
```

## License Number Format

License numbers are automatically generated using the format:
```
{TYPE}{YEAR}{RANDOM}
```

Where:
- `TYPE`: Two-letter prefix based on license type (RT, WH, MF, DS, RS, BR)
- `YEAR`: Last two digits of current year
- `RANDOM`: 8-character random hex string

Example: `RT24A1B2C3D4` (Retail license issued in 2024)

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200` - Success
- `201` - Created successfully
- `400` - Bad request (validation errors)
- `404` - Resource not found
- `500` - Internal server error

Error responses include descriptive messages:
```json
{
  "error": "Missing required field: business_name"
}
```

## Security Considerations

- Input validation for all fields
- Email and phone format validation
- SQL injection prevention through SQLAlchemy ORM
- Environment-based configuration
- Audit logging for all operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## License

This project is licensed under the MIT License.