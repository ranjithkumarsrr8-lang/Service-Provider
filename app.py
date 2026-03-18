import os
import datetime
import uuid
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Try to import flask_limiter, if not available, create a fallback
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

# Rate limiter for security (optional)
if LIMITER_AVAILABLE:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
else:
    # Fallback decorator if flask_limiter is not available
    def limiter_limit(limit_string):
        def decorator(f):
            return f
        return decorator

# In-memory storage (replace with database in production)
services = [
    {
        "id": "1",
        "name": "Electrician",
        "icon": "⚡",
        "description": "Electrical repairs, installations, and maintenance",
        "price_range": "₹300 - ₹1,500"
    },
    {
        "id": "2",
        "name": "Plumber",
        "icon": "🔧",
        "description": "Leak fixes, pipe repairs, and plumbing installations",
        "price_range": "₹250 - ₹1,200"
    },
    {
        "id": "3",
        "name": "Repair Technician",
        "icon": "🔨",
        "description": "Appliance repairs, AC service, and general maintenance",
        "price_range": "₹350 - ₹2,000"
    },
    {
        "id": "4",
        "name": "Carpenter",
        "icon": "🪚",
        "description": "Furniture repair, woodwork, and custom carpentry",
        "price_range": "₹400 - ₹2,500"
    },
    {
        "id": "5",
        "name": "Painter",
        "icon": "🎨",
        "description": "Interior and exterior painting services",
        "price_range": "₹500 - ₹3,000"
    },
    {
        "id": "6",
        "name": "Cleaning Service",
        "icon": "✨",
        "description": "Home cleaning, deep cleaning, and sanitization",
        "price_range": "₹200 - ₹1,000"
    }
]

service_providers = [
    {
        "id": "p1",
        "name": "Rajesh Kumar",
        "service_id": "1",
        "service_name": "Electrician",
        "rating": 4.8,
        "reviews": 127,
        "experience": "8 years",
        "location": "Koramangala, Bangalore",
        "phone": "+91 98765 43210",
        "image": "👨‍🔧",
        "available": True,
        "price_per_hour": 350,
        "lat": 12.9352,
        "lng": 77.6245
    },
    {
        "id": "p2",
        "name": "Suresh Patel",
        "service_id": "1",
        "service_name": "Electrician",
        "rating": 4.6,
        "reviews": 89,
        "experience": "5 years",
        "location": "Indiranagar, Bangalore",
        "phone": "+91 98765 43211",
        "image": "👨‍🔧",
        "available": True,
        "price_per_hour": 300,
        "lat": 12.9719,
        "lng": 77.6412
    },
    {
        "id": "p3",
        "name": "Anand Sharma",
        "service_id": "2",
        "service_name": "Plumber",
        "rating": 4.9,
        "reviews": 156,
        "experience": "12 years",
        "location": "HSR Layout, Bangalore",
        "phone": "+91 98765 43212",
        "image": "👨‍🔧",
        "available": True,
        "price_per_hour": 400,
        "lat": 12.9121,
        "lng": 77.6446
    },
    {
        "id": "p4",
        "name": "Priya Nair",
        "service_id": "2",
        "service_name": "Plumber",
        "rating": 4.7,
        "reviews": 94,
        "experience": "6 years",
        "location": "Whitefield, Bangalore",
        "phone": "+91 98765 43213",
        "image": "👩‍🔧",
        "available": True,
        "price_per_hour": 350,
        "lat": 12.9698,
        "lng": 77.7500
    },
    {
        "id": "p5",
        "name": "Venkatesh Iyer",
        "service_id": "3",
        "service_name": "Repair Technician",
        "rating": 4.8,
        "reviews": 203,
        "experience": "10 years",
        "location": "JP Nagar, Bangalore",
        "phone": "+91 98765 43214",
        "image": "👨‍🔧",
        "available": True,
        "price_per_hour": 450,
        "lat": 12.9063,
        "lng": 77.5857
    },
    {
        "id": "p6",
        "name": "Lakshmi Reddy",
        "service_id": "3",
        "service_name": "Repair Technician",
        "rating": 4.5,
        "reviews": 67,
        "experience": "4 years",
        "location": "Marathahalli, Bangalore",
        "phone": "+91 98765 43215",
        "image": "👩‍🔧",
        "available": False,
        "price_per_hour": 300,
        "lat": 12.9569,
        "lng": 77.7011
    },
    {
        "id": "p7",
        "name": "Ramesh Gupta",
        "service_id": "4",
        "service_name": "Carpenter",
        "rating": 4.9,
        "reviews": 112,
        "experience": "15 years",
        "location": "BTM Layout, Bangalore",
        "phone": "+91 98765 43216",
        "image": "👨‍🔧",
        "available": True,
        "price_per_hour": 500,
        "lat": 12.9166,
        "lng": 77.6101
    },
    {
        "id": "p8",
        "name": "Meena Joshi",
        "service_id": "5",
        "service_name": "Painter",
        "rating": 4.7,
        "reviews": 78,
        "experience": "7 years",
        "location": "Electronic City, Bangalore",
        "phone": "+91 98765 43217",
        "image": "👩‍🎨",
        "available": True,
        "price_per_hour": 350,
        "lat": 12.8458,
        "lng": 77.6602
    },
    {
        "id": "p9",
        "name": "Saroja Devi",
        "service_id": "6",
        "service_name": "Cleaning Service",
        "rating": 4.8,
        "reviews": 145,
        "experience": "5 years",
        "location": "Bannerghatta, Bangalore",
        "phone": "+91 98765 43218",
        "image": "👩‍🧹",
        "available": True,
        "price_per_hour": 250,
        "lat": 12.8000,
        "lng": 77.5770
    }
]

bookings = []
users = []
failed_login_attempts = {}  # Track failed login attempts for rate limiting

# Provider authentication storage
provider_credentials = {
    "p1": {"password_hash": generate_password_hash("rajesh123"), "phone": "+91 98765 43210"},
    "p2": {"password_hash": generate_password_hash("suresh123"), "phone": "+91 98765 43211"},
    "p3": {"password_hash": generate_password_hash("anand123"), "phone": "+91 98765 43212"},
    "p4": {"password_hash": generate_password_hash("priya123"), "phone": "+91 98765 43213"},
    "p5": {"password_hash": generate_password_hash("venkat123"), "phone": "+91 98765 43214"},
    "p6": {"password_hash": generate_password_hash("lakshmi123"), "phone": "+91 98765 43215"},
    "p7": {"password_hash": generate_password_hash("ramesh123"), "phone": "+91 98765 43216"},
    "p8": {"password_hash": generate_password_hash("meena123"), "phone": "+91 98765 43217"},
    "p9": {"password_hash": generate_password_hash("saroja123"), "phone": "+91 98765 43218"},
}

# Password validation function
def validate_password(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*)")
    
    return errors

def get_password_strength(password):
    """Get password strength score (0-100)"""
    score = 0
    if len(password) >= 8:
        score += 10
    if len(password) >= 12:
        score += 10
    if re.search(r'[a-z]', password):
        score += 15
    if re.search(r'[A-Z]', password):
        score += 15
    if re.search(r'[0-9]', password):
        score += 15
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 20
    return min(score, 100)

# Routes
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/register", methods=["POST"])
def register():
    """Register new user with strong password requirements"""
    # Apply rate limiting if available
    if LIMITER_AVAILABLE:
        @limiter.limit("5 per hour")
        def handler():
            pass
        handler()
    
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    
    # Validate input
    if not email or not password or not name or not phone:
        return jsonify({"error": "All fields are required"}), 400
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate name (at least 2 characters)
    if len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400
    
    # Validate phone (basic validation)
    if len(phone) < 10:
        return jsonify({"error": "Phone number must be at least 10 digits"}), 400
    
    # Validate password strength
    password_errors = validate_password(password)
    if password_errors:
        return jsonify({
            "error": "Password is too weak",
            "details": password_errors,
            "strength": get_password_strength(password)
        }), 400
    
    # Check if email already exists
    if any(u["email"] == email for u in users):
        return jsonify({"error": "Email already exists"}), 400
    
    # Create user with hashed password
    user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": generate_password_hash(password),
        "created_at": datetime.datetime.now().isoformat()
    }
    users.append(user)
    
    safe_user = {k: v for k, v in user.items() if k not in ["password_hash", "created_at"]}
    return jsonify({"user": safe_user}), 201


@app.route("/api/login", methods=["POST"])
def login():
    """Login with strong security checks"""
    # Apply rate limiting if available
    if LIMITER_AVAILABLE:
        @limiter.limit("10 per hour")
        def handler():
            pass
        handler()
    
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    # Validate input
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Check for brute force attempts
    if failed_login_attempts.get(email, 0) >= 5:
        return jsonify({"error": "Too many failed login attempts. Please try again later."}), 429
    
    # Find user
    user = next((u for u in users if u["email"] == email), None)
    
    if not user or not check_password_hash(user.get("password_hash", ""), password):
        # Increment failed attempts
        failed_login_attempts[email] = failed_login_attempts.get(email, 0) + 1
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Reset failed attempts on successful login
    failed_login_attempts[email] = 0
    
    safe_user = {k: v for k, v in user.items() if k not in ["password_hash", "created_at"]}
    return jsonify({"user": safe_user}), 200


@app.route("/api/services", methods=["GET"])
def get_services():
    return jsonify({"services": services})


@app.route("/api/providers", methods=["GET"])
def get_providers():
    service_id = request.args.get("service_id")
    location = request.args.get("location")
    
    filtered_providers = service_providers
    
    if service_id:
        filtered_providers = [p for p in filtered_providers if p["service_id"] == service_id]
    
    if location:
        filtered_providers = [p for p in filtered_providers if location.lower() in p["location"].lower()]
    
    return jsonify({"providers": filtered_providers})


@app.route("/api/provider/<provider_id>", methods=["GET"])
def get_provider(provider_id):
    provider = next((p for p in service_providers if p["id"] == provider_id), None)
    if provider:
        return jsonify({"provider": provider})
    return jsonify({"error": "Provider not found"}), 404


@app.route("/api/book", methods=["POST"])
def create_booking():
    data = request.get_json()
    
    required_fields = ["provider_id", "customer_name", "customer_phone", "address", "date", "time"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    provider = next((p for p in service_providers if p["id"] == data["provider_id"]), None)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404
    
    booking = {
        "id": str(uuid.uuid4()),
        "provider_id": data["provider_id"],
        "provider_name": provider["name"],
        "service_name": provider["service_name"],
        "customer_name": data["customer_name"],
        "customer_phone": data["customer_phone"],
        "address": data["address"],
        "date": data["date"],
        "time": data["time"],
        "notes": data.get("notes", ""),
        "status": "confirmed",
        "created_at": datetime.datetime.now().isoformat(),
        "price_per_hour": provider["price_per_hour"]
    }
    
    bookings.append(booking)
    
    return jsonify({
        "message": "Booking confirmed successfully!",
        "booking": booking
    })


@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    phone = request.args.get("phone")
    if phone:
        user_bookings = [b for b in bookings if b["customer_phone"] == phone]
        return jsonify({"bookings": user_bookings})
    return jsonify({"bookings": bookings})


@app.route("/api/booking/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    global bookings
    booking = next((b for b in bookings if b["id"] == booking_id), None)
    if booking:
        bookings = [b for b in bookings if b["id"] != booking_id]
        return jsonify({"message": "Booking cancelled successfully"})
    return jsonify({"error": "Booking not found"}), 404


@app.route("/api/provider/<provider_id>/bookings", methods=["GET"])
def get_provider_bookings(provider_id):
    provider = next((p for p in service_providers if p["id"] == provider_id), None)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404
    
    provider_bookings = [b for b in bookings if b["provider_id"] == provider_id]
    return jsonify({"bookings": provider_bookings})


@app.route("/api/provider/login", methods=["POST"])
def provider_login():
    """Provider login with phone and password"""
    data = request.get_json()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    
    if not phone or not password:
        return jsonify({"error": "Phone and password are required"}), 400
    
    # Find provider by phone
    provider = None
    provider_id = None
    for pid, creds in provider_credentials.items():
        if creds["phone"] == phone:
            provider_id = pid
            break
    
    if not provider_id:
        return jsonify({"error": "Provider not found"}), 404
    
    provider = next((p for p in service_providers if p["id"] == provider_id), None)
    if not provider:
        return jsonify({"error": "Provider profile not found"}), 404
    
    # Check password
    if not check_password_hash(provider_credentials[provider_id]["password_hash"], password):
        return jsonify({"error": "Invalid password"}), 401
    
    return jsonify({
        "success": True,
        "provider": {
            "id": provider["id"],
            "name": provider["name"],
            "service_name": provider["service_name"],
            "phone": provider["phone"],
            "rating": provider["rating"],
            "reviews": provider["reviews"],
            "experience": provider["experience"],
            "location": provider["location"],
            "available": provider["available"],
            "price_per_hour": provider["price_per_hour"]
        }
    })


@app.route("/api/provider/<provider_id>/dashboard", methods=["GET"])
def provider_dashboard(provider_id):
    """Get provider dashboard data"""
    provider = next((p for p in service_providers if p["id"] == provider_id), None)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404
    
    # Get provider's bookings
    provider_bookings = [b for b in bookings if b["provider_id"] == provider_id]
    
    # Calculate stats
    total_bookings = len(provider_bookings)
    completed_bookings = len([b for b in provider_bookings if b["status"] == "completed"])
    pending_bookings = len([b for b in provider_bookings if b["status"] == "confirmed"])
    cancelled_bookings = len([b for b in provider_bookings if b["status"] == "cancelled"])
    
    # Calculate earnings (simplified)
    earnings = sum(b["price_per_hour"] * 2 for b in provider_bookings if b["status"] == "completed")  # Assuming 2-hour jobs
    
    return jsonify({
        "provider": provider,
        "stats": {
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "pending_bookings": pending_bookings,
            "cancelled_bookings": cancelled_bookings,
            "earnings": earnings
        },
        "recent_bookings": provider_bookings[-5:]  # Last 5 bookings
    })


@app.route("/api/provider/<provider_id>/availability", methods=["PUT"])
def update_provider_availability(provider_id):
    """Update provider availability status"""
    provider = next((p for p in service_providers if p["id"] == provider_id), None)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404
    
    data = request.get_json()
    available = data.get("available")
    
    if available is None:
        return jsonify({"error": "Availability status is required"}), 400
    
    provider["available"] = bool(available)
    return jsonify({"message": "Availability updated", "available": provider["available"]})


@app.route("/api/provider/<provider_id>/profile", methods=["PUT"])
def update_provider_profile(provider_id):
    """Update provider profile information"""
    provider = next((p for p in service_providers if p["id"] == provider_id), None)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ["price_per_hour", "experience", "location"]
    for field in allowed_fields:
        if field in data:
            if field == "price_per_hour":
                try:
                    provider[field] = int(data[field])
                except ValueError:
                    return jsonify({"error": "Invalid price format"}), 400
            else:
                provider[field] = data[field]
    
    return jsonify({"message": "Profile updated", "provider": provider})


@app.route("/api/provider/<provider_id>/password", methods=["PUT"])
def change_provider_password(provider_id):
    """Change provider password"""
    if provider_id not in provider_credentials:
        return jsonify({"error": "Provider not found"}), 404
    
    data = request.get_json()
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    
    if not current_password or not new_password:
        return jsonify({"error": "Current and new password are required"}), 400
    
    # Validate current password
    if not check_password_hash(provider_credentials[provider_id]["password_hash"], current_password):
        return jsonify({"error": "Current password is incorrect"}), 401
    
    # Validate new password strength
    password_errors = validate_password(new_password)
    if password_errors:
        return jsonify({
            "error": "New password is too weak",
            "details": password_errors
        }), 400
    
    # Update password
    provider_credentials[provider_id]["password_hash"] = generate_password_hash(new_password)
    return jsonify({"message": "Password changed successfully"})


@app.route("/api/booking/<booking_id>/status", methods=["PUT"])
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get("status", "")
    
    booking = next((b for b in bookings if b["id"] == booking_id), None)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    if new_status in ["confirmed", "completed", "cancelled"]:
        booking["status"] = new_status
        return jsonify({"message": "Status updated", "booking": booking})
    
    return jsonify({"error": "Invalid status"}), 400


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"services": services, "providers": service_providers})
    
    matched_services = [s for s in services if query in s["name"].lower() or query in s["description"].lower()]
    matched_providers = [p for p in service_providers if query in p["name"].lower() or query in p["service_name"].lower()]
    
    return jsonify({
        "services": matched_services,
        "providers": matched_providers
    })


if __name__ == "__main__":
    print()
    print("  ========================================")
    print("   Local Services App")
    print("   Book nearby services quickly!")
    print("  ========================================")
    print("   Status: ONLINE")
    print("   Interface: http://localhost:5000")
    print("  ========================================")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
