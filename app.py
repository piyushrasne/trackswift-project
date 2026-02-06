# Project main files are here i import flask and other required modules 
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json, os, datetime, re, random
from werkzeug.utils import secure_filename

# Initialize the application
app = Flask(__name__)
app.secret_key = 'trackswift_secret'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Check if upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Data file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PARCEL_FILE = os.path.join(DATA_DIR, 'parcels.json')
CHANGE_REQUESTS_FILE = os.path.join(DATA_DIR, 'change_requests.json')

# Helper function to get parcel data
def load_parcels():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(PARCEL_FILE):
        with open(PARCEL_FILE, 'w') as f:
            json.dump([], f)
    with open(PARCEL_FILE, 'r') as f:
        data = json.load(f)
        # Ensure data consistency
        for p in data:
            if 'image' not in p: p['image'] = ''
            if 'start_address' not in p: p['start_address'] = ''
            if 'end_address' not in p: p['end_address'] = p.get('address', '')
            if 'tracking_history' not in p: p['tracking_history'] = []
            if 'current_location' not in p: p['current_location'] = p.get('address', '')
        return data

# Helper function to save parcel data
def save_parcels(parcels):
    with open(PARCEL_FILE, 'w') as f:
        json.dump(parcels, f, indent=4)

# Helper function to get change requests
def load_change_requests():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(CHANGE_REQUESTS_FILE):
        with open(CHANGE_REQUESTS_FILE, 'w') as f:
            json.dump([], f)
    with open(CHANGE_REQUESTS_FILE, 'r') as f:
        return json.load(f)

# Helper function to save change requests
def save_change_requests(requests):
    with open(CHANGE_REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=4)

# --- Application Routes ---

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Handle User Feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    email = request.form.get('email')
    message = request.form.get('message')
    flash('Thank you for your feedback!')
    return redirect('/')

# Tracking Page
@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        query = request.form['tracking_id'].strip().lower()
        parcels = load_parcels()
        
        found_parcel = None
        
        # Search by ID first
        for parcel in parcels:
            if parcel['id'].lower() == query:
                found_parcel = parcel
                break
        
        # Search by Name if not found
        if not found_parcel:
            for parcel in parcels:
                if query in parcel['name'].lower():
                    found_parcel = parcel
                    break
        
        if found_parcel:
             return render_template('track.html', parcel=found_parcel)
             
        return render_template('track.html', not_found=True)
    return render_template('track.html')

# Handle Address Change Requests
@app.route('/request_change', methods=['POST'])
def request_change():
    request_data = {
        'id': request.form['id'],
        'new_address': request.form['new_address'],
        'new_phone': request.form['new_phone'],
        'new_region': request.form['new_region']
    }
    requests = load_change_requests()
    requests.append(request_data)
    save_change_requests(requests)
    flash('Change Request Sent to Admin.')
    return redirect('/track')

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect('/dashboard')
        flash('Invalid credentials')
    return render_template('login.html')

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')
    parcels = load_parcels()
    requests_count = len(load_change_requests())
    return render_template('dashboard.html', parcels=parcels, requests_count=requests_count)

# Add New Parcel Logic
@app.route('/add_parcel', methods=['POST'])
def add_parcel():
    if not session.get('admin'):
        return redirect('/login')
    new_parcel = {
        'id': request.form['id'] or ('TRK' + str(datetime.datetime.now().timestamp()).replace('.', '')[-5:]),
        'name': request.form['name'],
        'status': request.form['status'],
        'address': request.form['address'],
        'start_address': request.form.get('start_address', ''),
        'end_address': request.form.get('end_address', ''),
        'price': request.form['price'],
        'phone': request.form['phone'],
        'email': request.form['email'],
        'payment_type': request.form['payment_type'],
        'region': request.form['region'],
        'image': '',
        'tracking_history': [],
        'current_location': request.form.get('start_address', '')
    }
    
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_parcel['image'] = 'uploads/' + filename
    parcels = load_parcels()
    parcels.append(new_parcel)
    save_parcels(parcels)
    return redirect('/dashboard')

# Approve Parcel Request
@app.route('/approve_parcel/<id>')
def approve_parcel(id):
    if not session.get('admin'):
        return redirect('/login')
    parcels = load_parcels()
    for p in parcels:
        if p['id'] == id:
            p['status'] = 'Pending Pickup'
            if not p['tracking_history']:
                p['tracking_history'].append({'status': 'Request Approved', 'location': 'Admin Center', 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
    save_parcels(parcels)
    flash('Parcel Request Approved!')
    return redirect('/dashboard')

# Reject Parcel Request
@app.route('/reject_parcel/<id>')
def reject_parcel(id):
    if not session.get('admin'):
        return redirect('/login')
    parcels = load_parcels()
    parcels = [p for p in parcels if p['id'] != id]
    save_parcels(parcels)
    flash('Parcel Request Rejected.')
    return redirect('/dashboard')

# Delete Parcel
@app.route('/delete_parcel', methods=['POST'])
def delete_parcel():
    if not session.get('admin'):
        return redirect('/login')
    parcel_id = request.form['id']
    parcels = load_parcels()
    parcels = [parcel for parcel in parcels if parcel['id'] != parcel_id]
    save_parcels(parcels)
    return redirect('/dashboard')

# Create Parcel Page
@app.route('/create_parcel', methods=['GET', 'POST'])
def create_parcel():
    if request.method == 'POST':
        # Generate random ID
        parcel_id = 'TRK' + str(random.randint(10000, 99999))
        
        new_parcel = {
            'id': parcel_id,
            'name': request.form['sender_name'],
            'status': 'Pending Approval',
            'address': request.form['address'],
            'start_address': request.form['start_address'],
            'end_address': request.form['address'],
            'price': 'Calculate...',
            'phone': request.form['phone'],
            'email': request.form['email'],
            'payment_type': 'TBD',
            'region': request.form.get('region', 'India'),
            'image': '',
            'tracking_history': [{'status': 'Order Placed', 'location': 'Online', 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}],
            'current_location': 'Sender Location'
        }

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_parcel['image'] = 'uploads/' + filename
        
        parcels = load_parcels()
        parcels.append(new_parcel)
        save_parcels(parcels)
        return render_template('create_parcel.html', success=True, tracking_id=parcel_id)
    return render_template('create_parcel.html')

# Edit Parcel Details
@app.route('/edit_parcel/<id>', methods=['GET', 'POST'])
def edit_parcel(id):
    if not session.get('admin'):
        return redirect('/login')
    
    parcels = load_parcels()
    parcel = next((p for p in parcels if p['id'] == id), None)
    
    if not parcel:
        return "Parcel not found", 404

    if request.method == 'POST':
        parcel['status'] = request.form['status']
        parcel['current_location'] = request.form['current_location']
        parcel['start_address'] = request.form['start_address']
        parcel['end_address'] = request.form['end_address']
        
        # Add tracking history
        new_status_header = request.form.get('new_status_header')
        if new_status_header:
            new_desc = request.form.get('new_description', '')
            new_date = request.form.get('new_date')
            new_time = request.form.get('new_time')
            
            # Format date and time
            formatted_ts = f"{new_date} {new_time}"
            try:
                dt_obj = datetime.datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
                day = dt_obj.day
                suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                formatted_ts = dt_obj.strftime(f"%a, {day}{suffix} %b '%y - %I:%M%p").lower()
            except:
                pass

            parcel['tracking_history'].append({
                'status': new_status_header,
                'subtext': request.form.get('new_subtext', ''),
                'description': new_desc,
                'location': request.form.get('new_location', parcel['current_location']),
                'timestamp': formatted_ts
            })
            
        save_parcels(parcels)
        flash('Parcel Updated Successfully')
        return redirect(url_for('edit_parcel', id=id))
        
    return render_template('edit_parcel.html', parcel=parcel)

# Handle Admin Requests
@app.route('/handle_requests', methods=['GET', 'POST'])
def handle_requests():
    if not session.get('admin'):
        return redirect('/login')
    requests = load_change_requests()
    parcels = load_parcels()
    if request.method == 'POST':
        action = request.form['action']
        parcel_id = request.form['id']
        if action == 'approve':
            for parcel in parcels:
                if parcel['id'] == parcel_id:
                    for req in requests:
                        if req['id'] == parcel_id:
                            if req['new_address']:
                                parcel['address'] = req['new_address']
                            if req['new_phone']:
                                parcel['phone'] = req['new_phone']
                            if req['new_region']:
                                parcel['region'] = req['new_region']
            requests = [r for r in requests if r['id'] != parcel_id]
            save_parcels(parcels)
        elif action == 'reject':
            requests = [r for r in requests if r['id'] != parcel_id]
        save_change_requests(requests)
        return redirect('/handle_requests')
    return render_template('handle_requests.html', requests=requests, parcels=parcels)

# Print Label
@app.route('/print_label/<id>')
def print_label(id):
    if not session.get('admin'):
        return redirect('/login')
    parcels = load_parcels()
    parcel = next((p for p in parcels if p['id'] == id), None)
    if not parcel:
        return "Parcel not found", 404
    return render_template('print_label.html', parcel=parcel, date=datetime.datetime.now().strftime("%Y-%m-%d"))

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

# Helper function for Chatbot API
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'reply': "I didn't catch that. Could you say it again?"})

    # Look for tracking ID in message
    tracking_match = re.search(r'(TRK\d+)', message, re.IGNORECASE)
    
    if tracking_match:
        tracking_id = tracking_match.group(1).upper()
        parcels = load_parcels()
        parcel = next((p for p in parcels if p['id'] == tracking_id), None)
        
        if parcel:
            history = parcel.get('tracking_history', [])
            latest_status = history[-1]['status'] if history else parcel['status']
            latest_loc = history[-1]['location'] if history else parcel['current_location']
            
            return jsonify({
                'reply': f"📦 **Parcel {tracking_id} Found!**<br>Status: **{latest_status}**<br>Location: {latest_loc}<br><a href='/track' class='chat-link'>View Details</a>"
            })
        else:
            return jsonify({'reply': f"❌ I couldn't find any parcel with ID **{tracking_id}**. Please check and try again."})

    # Standard responses
    msg_lower = message.lower()
    
    if 'track' in msg_lower or 'status' in msg_lower:
        return jsonify({'reply': "To track a parcel, please enter your **Tracking ID** (e.g., TRK12345)."})
        
    elif 'send' in msg_lower or 'ship' in msg_lower or 'create' in msg_lower:
        return jsonify({'reply': "🚀 You can send a parcel easily! <a href='/create_parcel' class='chat-link'>Click here to Ship Now</a>."})
        
    elif 'price' in msg_lower or 'cost' in msg_lower or 'rate' in msg_lower:
        return jsonify({'reply': "💰 Shipping rates depend on weight and distance. You can calculate it on the <a href='/create_parcel' class='chat-link'>Send Parcel</a> page."})
        
    elif 'contact' in msg_lower or 'call' in msg_lower or 'support' in msg_lower:
        return jsonify({'reply': "📞 You can contact support at **+91 96572 65104** or <a href='https://wa.me/919657265104' target='_blank' class='chat-link'>Chat on WhatsApp</a>."})

    elif 'hi' in msg_lower or 'hello' in msg_lower or 'hey' in msg_lower:
        return jsonify({'reply': "👋 Hi there! I'm your TrackSwift Assistant. How can I help you today?"})

    else:
        return jsonify({'reply': "🤔 I'm not sure about that. Try asking about **tracking**, **shipping**, or **contacting support**."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
