
import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PARCEL_FILE = os.path.join(DATA_DIR, 'parcels.json')
CHANGE_REQUESTS_FILE = os.path.join(DATA_DIR, 'change_requests.json')

def seed_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Clear existing data
    with open(CHANGE_REQUESTS_FILE, 'w') as f:
        json.dump([], f)

    parcels = []
    
    # Diverse Indian Names (North, South, East, West)
    first_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
        "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Anika", "Navya", "Angel", "Myra", "Riya",
        "Rohan", "Vikram", "Neha", "Pooja", "Suresh", "Ramesh", "Geeta", "Sita", "Mohan", "Sohan"
    ]
    last_names = [
        "Sharma", "Gupta", "Patel", "Kumar", "Singh", "Reddy", "Joshi", "Malhotra", "Choudhury", "Iyer",
        "Verma", "Mehta", "Nair", "Das", "Chatterjee", "Banerjee", "Fernandes", "Khan", "Ali", "Mishra",
        "Yadav", "Gowda", "Rao", "Shetty", "Deshmukh", "Pawar", "Bhat", "Kulkarni", "Jain", "Agarwal"
    ]
    
    # Diverse Locations and Hubs
    locations = [
        {"city": "Mumbai", "state": "Maharashtra", "hubs": ["Bhiwandi Hub", "Lower Parel Hub", "Andheri East Hub"]},
        {"city": "Delhi", "state": "Delhi", "hubs": ["Okhla Phase III", "Dwarka Sector 9", "Connaught Place"]},
        {"city": "Bangalore", "state": "Karnataka", "hubs": ["Electronic City", "Whitefield", "Koramangala"]},
        {"city": "Hyderabad", "state": "Telangana", "hubs": ["Madhapur", "Banjara Hills", "Secunderabad"]},
        {"city": "Chennai", "state": "Tamil Nadu", "hubs": ["Guindy", "T Nagar", "Anna Nagar"]},
        {"city": "Kolkata", "state": "West Bengal", "hubs": ["Salt Lake", "Park Street", "Howrah"]},
        {"city": "Pune", "state": "Maharashtra", "hubs": ["Hinjewadi", "Viman Nagar", "Kothrud"]},
        {"city": "Ahmedabad", "state": "Gujarat", "hubs": ["SG Highway", "Maninagar", "Satellite"]},
        {"city": "Jaipur", "state": "Rajasthan", "hubs": ["Malviya Nagar", "Vaishali Nagar", "C Scheme"]},
        {"city": "Lucknow", "state": "Uttar Pradesh", "hubs": ["Gomti Nagar", "Hazratganj", "Alambagh"]}
    ]

    logistics_partners = ["Ekart Logistics", "BlueDart Express", "Delhivery", "Ecom Express", "Xpressbees", "Shadowfax", "Gati"]

    for i in range(25): # Generate 25 parcels
        pid = f"TRK2026{random.randint(10000, 99999)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        dest = random.choice(locations)
        origin = random.choice(locations)
        while origin == dest: # Ensure different origin/dest
            origin = random.choice(locations)
            
        addr = f"Flat {random.randint(1, 900)}, {random.choice(['Green Apts', 'Sunshine Tower', 'Galaxy Heights', 'Palm Grove', 'Royal Enclave'])}, {dest['city']}, {dest['state']}"
        start_addr = f"Main Warehouse, {origin['hubs'][0]}, {origin['city']}, {origin['state']}"
        
        courier = random.choice(logistics_partners)
        agent = f"{random.choice(first_names)} ({random.randint(7000000000, 9999999999)})"

        # Construct History
        history = [
            {
                "status": "Order Confirmed",
                "timestamp": "Mon, 26th Jan '26 - 09:30am",
                "location": "Online",
                "description": "Your Order has been placed.",
                "subtext": f"Order ID #OD{random.randint(1000000, 9999999)}"
            },
            {
                "status": "Picked Up",
                "timestamp": "Tue, 27th Jan '26 - 02:15pm",
                "location": start_addr,
                "description": "Seller has handed over the package.",
                "subtext": f"{courier}"
            },
            {
                "status": "In Transit",
                "timestamp": "Wed, 28th Jan '26 - 11:00am",
                "location": f"{random.choice(origin['hubs'])}, {origin['city']}",
                "description": "Arrived at Origin Facility",
                "subtext": "Processing"
            },
            {
                "status": "Shipped",
                "timestamp": "Thu, 29th Jan '26 - 05:45pm",
                "location": f"{random.choice(dest['hubs'])}, {dest['city']}",
                "description": "Arrived at Destination Hub",
                "subtext": f"{courier} Facility"
            },
            {
                "status": "Out For Delivery",
                "timestamp": "Fri, 30th Jan '26 - 08:30am",
                "location": f"{dest['city']} Delivery Center",
                "description": "Your item is out for delivery",
                "subtext": f"Agent: {agent}"
            },
            {
                "status": "Delivered",
                "timestamp": "Fri, 30th Jan '26 - 06:20pm",
                "location": addr,
                "description": "Your item has been delivered",
                "subtext": "Signed by: Receiver"
            }
        ]

        parcel = {
            'id': pid,
            'name': name,
            'status': 'Delivered',
            'address': addr,
            'start_address': start_addr,
            'end_address': addr,
            'price': f"₹ {random.choice([499, 999, 1299, 2499, 5999])}",
            'phone': f"+91 {random.randint(7000000000, 9999999999)}",
            'email': f"{name.lower().replace(' ', '.')}@example.com",
            'payment_type': random.choice(['Prepaid', 'Postpaid', 'COD']),
            'region': 'Domestic',
            'image': 'uploads/parcel_box.png',
            'tracking_history': history,
            'current_location': addr
        }
        parcels.append(parcel)

    with open(PARCEL_FILE, 'w') as f:
        json.dump(parcels, f, indent=4)
    
    print(f"Successfully seeded {len(parcels)} diverse parcels into {PARCEL_FILE}")

if __name__ == "__main__":
    seed_data()
