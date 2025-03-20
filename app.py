from flask import Flask, request, render_template, redirect, jsonify
import os
import json
import hashlib
import pyqrcode
import shutil

app = Flask(__name__)
DATA_FILE = 'data/short_links.json'
QR_DIR = "static/qrcodes"
PUBLIC_URL = "https://qrcode-fw9c.onrender.com/"  # Change this to your actual Render domain

# Ensure required directories exist
os.makedirs("data", exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

# Load data from JSON file (Persistent Storage Alternative: Use a Database)
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}  # If file is corrupted, return empty dict
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Generate a short URL using a hash function
def generate_short_url(property_name):
    return hashlib.md5(property_name.encode()).hexdigest()[:6]

# Generate QR Code
def generate_qr_code(short_url):
    qr_path = os.path.join(QR_DIR, f"{short_url}.png")
    
    # Create QR code only if it doesn't exist
    if not os.path.exists(qr_path):
        qr = pyqrcode.create(f"{PUBLIC_URL}{short_url}")
        qr.png(qr_path, scale=6)
    
    return qr_path

@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()
    
    if request.method == 'POST':
        property_name = request.form.get('property_name')
        destination_url = request.form.get('destination_url')
        
        if not property_name or not destination_url:
            return render_template("index.html", error="Both fields are required!")

        if property_name in data:
            short_url = data[property_name]['short_url']
            data[property_name]['destination_url'] = destination_url  # Update existing link
        else:
            short_url = generate_short_url(property_name)
            data[property_name] = {'short_url': short_url, 'destination_url': destination_url}
        
        save_data(data)
        qr_code_path = generate_qr_code(short_url)
        
        return render_template("index.html", short_url=short_url, qr_code_path=qr_code_path, public_url=PUBLIC_URL)
    
    return render_template("index.html")

@app.route('/<short_url>')
def redirect_url(short_url):
    data = load_data()
    
    for details in data.values():
        if details['short_url'] == short_url:
            return redirect(details['destination_url'])
    
    return "Short URL not found", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render-assigned PORT
    app.run(host="0.0.0.0", port=port, debug=True)
