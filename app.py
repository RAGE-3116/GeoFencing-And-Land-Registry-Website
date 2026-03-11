from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Database configuration
DATABASE = 'land_registry.db'

# Cloudinary configuration (optional - app works without it)
CLOUDINARY_ENABLED = False
try:
    import cloudinary
    import cloudinary.uploader
    
    # Try to configure from environment variables
    cloud_name = os.getenv('dxlwrxwjl')
    api_key = os.getenv('925297674287918')
    api_secret = os.getenv('v7L380npsH5M8UsU5iBrV4IhDkk')
    
    if all([cloud_name, api_key, api_secret]):
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        CLOUDINARY_ENABLED = True
        print("✓ Cloudinary configured successfully")
    else:
        print("⚠ Cloudinary not configured - app will work without cloud backup")
except ImportError:
    print("⚠ Cloudinary library not installed - app will work without cloud backup")

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            property_name TEXT NOT NULL,
            coords TEXT NOT NULL,
            verified INTEGER DEFAULT 0,
            cloudinary_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create auctions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            property_name TEXT NOT NULL,
            owner TEXT NOT NULL,
            starting_bid REAL NOT NULL,
            current_bid REAL NOT NULL,
            description TEXT,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            status TEXT DEFAULT 'active',
            winner TEXT,
            cloudinary_backup_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_id) REFERENCES properties(id)
        )
    ''')
    
    # Create bids table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auction_id INTEGER NOT NULL,
            bidder TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp REAL NOT NULL,
            FOREIGN KEY (auction_id) REFERENCES auctions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper function to get database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Cloudinary backup function
def backup_to_cloudinary(data_type, data):
    """Backup data to Cloudinary as JSON text file"""
    if not CLOUDINARY_ENABLED:
        return None
    
    try:
        # Convert data to JSON string
        json_data = json.dumps(data, indent=2)
        
        # Create a temporary file
        temp_filename = f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        temp_path = f"/tmp/{temp_filename}"
        
        with open(temp_path, 'w') as f:
            f.write(json_data)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            temp_path,
            resource_type="raw",
            public_id=f"land_registry_backup/{data_type}_latest",
            overwrite=True,
            folder="land_registry_backup"
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return result.get('secure_url')
    except Exception as e:
        print(f"Cloudinary backup error: {e}")
        return None

# Serve HTML files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# API: Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        
        # Backup to Cloudinary
        cursor.execute('SELECT id, username, created_at FROM users')
        all_users = [dict(row) for row in cursor.fetchall()]
        backup_url = backup_to_cloudinary('users', all_users)
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Signup successful'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'success': True, 'username': username})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# API: Get all properties
@app.route('/api/properties', methods=['GET'])
def get_properties():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM properties')
    properties = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(properties)

# API: Add property
@app.route('/api/add-property', methods=['POST'])
def add_property():
    data = request.json
    owner = data.get('owner')
    property_name = data.get('property_name')
    coords = data.get('coords')
    
    if not all([owner, property_name, coords]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400
    
    try:
        # Validate JSON coords
        json.loads(coords)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO properties (owner, property_name, coords, verified) VALUES (?, ?, ?, 0)',
            (owner, property_name, coords)
        )
        property_id = cursor.lastrowid
        conn.commit()
        
        # Backup to Cloudinary
        cursor.execute('SELECT * FROM properties')
        all_properties = [dict(row) for row in cursor.fetchall()]
        backup_url = backup_to_cloudinary('properties', all_properties)
        
        if backup_url:
            cursor.execute('UPDATE properties SET cloudinary_url = ? WHERE id = ?', (backup_url, property_id))
            conn.commit()
        
        cursor.execute('SELECT * FROM properties WHERE id = ?', (property_id,))
        new_property = dict(cursor.fetchone())
        conn.close()
        
        return jsonify({'success': True, 'message': 'Property added successfully', 'property': new_property})
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'Invalid JSON format for coordinates'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: Verify property
@app.route('/api/verify-property', methods=['POST'])
def verify_property():
    data = request.json
    property_id = data.get('id')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE properties SET verified = 1 WHERE id = ?', (property_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Property not found'}), 404
        
        # Backup to Cloudinary
        cursor.execute('SELECT * FROM properties')
        all_properties = [dict(row) for row in cursor.fetchall()]
        backup_to_cloudinary('properties', all_properties)
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Property verified'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: Get all auctions
@app.route('/api/auctions', methods=['GET'])
def get_auctions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM auctions')
    auctions = [dict(row) for row in cursor.fetchall()]
    
    # Get bids for each auction
    for auction in auctions:
        cursor.execute(
            'SELECT bidder, amount, timestamp FROM bids WHERE auction_id = ? ORDER BY amount DESC',
            (auction['id'],)
        )
        auction['bids'] = [dict(row) for row in cursor.fetchall()]
    
    # Check for expired auctions
    current_time = datetime.now().timestamp()
    properties_updated = False
    
    for auction in auctions:
        if auction['end_time'] < current_time and auction['status'] == 'active':
            cursor.execute('UPDATE auctions SET status = ? WHERE id = ?', ('ended', auction['id']))
            auction['status'] = 'ended'
            
            if auction['bids']:
                winner = auction['bids'][0]['bidder']
                cursor.execute('UPDATE properties SET owner = ? WHERE id = ?', (winner, auction['property_id']))
                cursor.execute('UPDATE auctions SET winner = ? WHERE id = ?', (winner, auction['id']))
                auction['winner'] = winner
                properties_updated = True
    
    conn.commit()
    
    # Backup if properties were updated
    if properties_updated:
        cursor.execute('SELECT * FROM properties')
        all_properties = [dict(row) for row in cursor.fetchall()]
        backup_to_cloudinary('properties', all_properties)
    
    conn.close()
    
    return jsonify(auctions)

# API: Create auction
@app.route('/api/create-auction', methods=['POST'])
def create_auction():
    data = request.json
    property_id = data.get('property_id')
    starting_bid = data.get('starting_bid')
    duration_hours = data.get('duration_hours')
    description = data.get('description', '')
    
    if not all([property_id, starting_bid, duration_hours]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM properties WHERE id = ?', (property_id,))
        property_obj = cursor.fetchone()
        
        if not property_obj:
            conn.close()
            return jsonify({'success': False, 'message': 'Property not found'}), 404
        
        property_dict = dict(property_obj)
        
        if property_dict['verified'] != 1:
            conn.close()
            return jsonify({'success': False, 'message': 'Only verified properties can be auctioned'}), 400
        
        cursor.execute('SELECT * FROM auctions WHERE property_id = ? AND status = ?', (property_id, 'active'))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Property already in auction'}), 400
        
        current_time = datetime.now().timestamp()
        end_time = current_time + (float(duration_hours) * 3600)
        
        cursor.execute('''
            INSERT INTO auctions (property_id, property_name, owner, starting_bid, current_bid,
                                description, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (property_id, property_dict['property_name'], property_dict['owner'],
              float(starting_bid), float(starting_bid), description, current_time, end_time, 'active'))
        
        auction_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM auctions WHERE id = ?', (auction_id,))
        new_auction = dict(cursor.fetchone())
        new_auction['bids'] = []
        
        # Backup to Cloudinary
        cursor.execute('SELECT * FROM auctions')
        all_auctions = [dict(row) for row in cursor.fetchall()]
        backup_to_cloudinary('auctions', all_auctions)
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Auction created successfully', 'auction': new_auction})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    # API: Delete property
@app.route('/api/delete-property', methods=['POST'])
def delete_property():
    data = request.json
    property_id = data.get('id')
    owner = data.get('owner')
    
    if not all([property_id, owner]):
        return jsonify({'success': False, 'message': 'Property ID and owner required'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if property exists and belongs to user
        cursor.execute('SELECT * FROM properties WHERE id = ? AND owner = ?', (property_id, owner))
        property_obj = cursor.fetchone()
        
        if not property_obj:
            conn.close()
            return jsonify({'success': False, 'message': 'Property not found or does not belong to you'}), 404
        
        # Check if property is in active auction
        cursor.execute('SELECT * FROM auctions WHERE property_id = ? AND status = ?', (property_id, 'active'))
        active_auction = cursor.fetchone()
        
        if active_auction:
            conn.close()
            return jsonify({'success': False, 'message': 'Cannot delete property in active auction'}), 400
        
        # Delete property
        cursor.execute('DELETE FROM properties WHERE id = ?', (property_id,))
        conn.commit()
        
        # Backup to Cloudinary if enabled
        if CLOUDINARY_ENABLED:
            cursor.execute('SELECT * FROM properties')
            all_properties = [dict(row) for row in cursor.fetchall()]
            backup_to_cloudinary('properties', all_properties)
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Property deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: Delete user account
@app.route('/api/delete-account', methods=['POST'])
def delete_account():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Verify user credentials
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Check for active auctions owned by user
        cursor.execute('''
            SELECT COUNT(*) as count FROM auctions 
            WHERE owner = ? AND status = ?
        ''', (username, 'active'))
        active_auctions = cursor.fetchone()['count']
        
        if active_auctions > 0:
            conn.close()
            return jsonify({
                'success': False, 
                'message': 'Cannot delete account with active auctions. Please wait for auctions to end.'
            }), 400
        
        # Delete user's bids
        cursor.execute('DELETE FROM bids WHERE bidder = ?', (username,))
        
        # Delete user's properties
        cursor.execute('DELETE FROM properties WHERE owner = ?', (username,))
        
        # Delete user's auctions
        cursor.execute('DELETE FROM auctions WHERE owner = ?', (username,))
        
        # Delete user account
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        
        conn.commit()
        
        # Backup to Cloudinary if enabled
        if CLOUDINARY_ENABLED:
            cursor.execute('SELECT * FROM users')
            all_users = [dict(row) for row in cursor.fetchall()]
            backup_to_cloudinary('users', all_users)
            
            cursor.execute('SELECT * FROM properties')
            all_properties = [dict(row) for row in cursor.fetchall()]
            backup_to_cloudinary('properties', all_properties)
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
# API: Place bid
@app.route('/api/bid', methods=['POST'])
def place_bid():
    data = request.json
    auction_id = data.get('auction_id')
    bidder = data.get('bidder')
    amount = data.get('amount')
    
    if not all([auction_id, bidder, amount]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM auctions WHERE id = ?', (auction_id,))
        auction = cursor.fetchone()
        
        if not auction:
            conn.close()
            return jsonify({'success': False, 'message': 'Auction not found'}), 404
        
        auction_dict = dict(auction)
        current_time = datetime.now().timestamp()
        
        if auction_dict['end_time'] < current_time or auction_dict['status'] != 'active':
            conn.close()
            return jsonify({'success': False, 'message': 'Auction has ended'}), 400
        
        if float(amount) <= auction_dict['current_bid']:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'Bid must be higher than current bid of ${auction_dict["current_bid"]}'
            }), 400
        
        cursor.execute('INSERT INTO bids (auction_id, bidder, amount, timestamp) VALUES (?, ?, ?, ?)',
                      (auction_id, bidder, float(amount), current_time))
        cursor.execute('UPDATE auctions SET current_bid = ? WHERE id = ?', (float(amount), auction_id))
        
        conn.commit()
        
        # Backup to Cloudinary
        cursor.execute('SELECT * FROM bids')
        all_bids = [dict(row) for row in cursor.fetchall()]
        backup_to_cloudinary('bids', all_bids)
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'Bid placed successfully', 'current_bid': float(amount)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🏠 DIGITAL LAND REGISTRY - SERVER STARTING")
    print("="*50)
    print("✓ Database initialized")
    if CLOUDINARY_ENABLED:
        print("✓ Cloudinary configured - backups enabled")
    else:
        print("⚠ Cloudinary not configured - running without cloud backup")
    print("\n📍 Server starting...")
    print("\nPress CTRL+C to stop the server")
    print("="*50 + "\n")
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Use 0.0.0.0 to allow external connections (required for deployment)
    # debug=False for production, True for local development
    is_production = os.environ.get('RENDER', False)
    app.run(host='0.0.0.0', port=port, debug=not is_production)
