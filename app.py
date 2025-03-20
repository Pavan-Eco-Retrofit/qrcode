from flask import Flask, request, jsonify, render_template, redirect
import json
import hashlib
import pyqrcode
import os

app = Flask(__name__)
DATA_FILE = 'short_links.json'

# Load existing data or create new
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            return {}  # Return an empty dictionary if the file is corrupted
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Generate short URL based on property name
def generate_short_url(property_name):
    return hashlib.md5(property_name.encode()).hexdigest()[:6]

PUBLIC_URL = "https://qrcode-fw9c.onrender.com/"  # Replace with your actual Render URL

def generate_qr_code(short_url):
    qr_path = f"static/qrcodes/{short_url}.png"
    if not os.path.exists("static/qrcodes"):
        os.makedirs("static/qrcodes")
    if not os.path.exists(qr_path):
        qr = pyqrcode.create(f"{PUBLIC_URL}{short_url}")
        qr.png(qr_path, scale=6)
    return qr_path


@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()
    
    if request.method == 'POST':
        property_name = request.form['property_name']
        destination_url = request.form['destination_url']
        
        if property_name in data:
            short_url = data[property_name]['short_url']
            data[property_name]['destination_url'] = destination_url  # Update only destination
        else:
            short_url = generate_short_url(property_name)
            data[property_name] = {'short_url': short_url, 'destination_url': destination_url}
        
        save_data(data)
        qr_code_path = generate_qr_code(short_url)  # Reuse the existing QR code
        
        return render_template("index.html", short_url=short_url, qr_code_path=qr_code_path)
    
    return render_template("index.html")

@app.route('/<short_url>')
def redirect_url(short_url):
    data = load_data()
    
    for property_name, details in data.items():
        if details['short_url'] == short_url:
            return redirect(details['destination_url'])
    
    return "Short URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
