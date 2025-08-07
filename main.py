from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os

app = Flask(__name__)
app.secret_key = 'trackswift_secret'

# Paths to JSON data files
PARCEL_FILE = 'data/parcels.json'
CHANGE_REQUESTS_FILE = 'data/change_requests.json'

# Utility functions to load/save parcels
def load_parcels():
    if not os.path.exists(PARCEL_FILE):
        with open(PARCEL_FILE, 'w') as f:
            json.dump([], f)
    with open(PARCEL_FILE, 'r') as f:
        return json.load(f)

def save_parcels(parcels):
    with open(PARCEL_FILE, 'w') as f:
        json.dump(parcels, f, indent=4)

# Utility functions to load/save change requests
def load_change_requests():
    if not os.path.exists(CHANGE_REQUESTS_FILE):
        with open(CHANGE_REQUESTS_FILE, 'w') as f:
            json.dump([], f)
    with open(CHANGE_REQUESTS_FILE, 'r') as f:
        return json.load(f)

def save_change_requests(requests):
    with open(CHANGE_REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=4)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']
        parcels = load_parcels()
        for parcel in parcels:
            if parcel['id'] == tracking_id:
                return render_template('track.html', parcel=parcel)
        return render_template('track.html', not_found=True)
    return render_template('track.html')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect('/dashboard')
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')
    parcels = load_parcels()
    requests_count = len(load_change_requests())
    return render_template('dashboard.html', parcels=parcels, requests_count=requests_count)

@app.route('/add_parcel', methods=['POST'])
def add_parcel():
    if not session.get('admin'):
        return redirect('/login')
    new_parcel = {
        'id': request.form['id'],
        'name': request.form['name'],
        'status': request.form['status'],
        'address': request.form['address'],
        'price': request.form['price'],
        'phone': request.form['phone'],
        'email': request.form['email'],
        'payment_type': request.form['payment_type'],
        'region': request.form['region']
    }
    parcels = load_parcels()
    parcels.append(new_parcel)
    save_parcels(parcels)
    return redirect('/dashboard')

@app.route('/delete_parcel', methods=['POST'])
def delete_parcel():
    if not session.get('admin'):
        return redirect('/login')
    parcel_id = request.form['id']
    parcels = load_parcels()
    parcels = [parcel for parcel in parcels if parcel['id'] != parcel_id]
    save_parcels(parcels)
    return redirect('/dashboard')

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
    return render_template('handle_requests.html', requests=requests)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)