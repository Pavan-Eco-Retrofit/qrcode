"""
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
"""

"""
from flask import Flask, request, render_template, redirect
import json
import hashlib
import pyqrcode
import base64
import io
import os

app = Flask(__name__)
DATA_FILE = "data/short_links.json"
PUBLIC_URL = "https://qrcode-fw9c.onrender.com/"  # Change this to your Render domain

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Load Data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

# Save Data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Generate Short URL
def generate_short_url(property_name):
    return hashlib.md5(property_name.encode()).hexdigest()[:6]

# Generate QR Code and Store as Base64 in JSON
def generate_qr_code_base64(short_url):
    qr = pyqrcode.create(f"{PUBLIC_URL}{short_url}")
    
    # Convert QR Code to Base64
    buffer = io.BytesIO()
    qr.png(buffer, scale=6)
    base64_qr = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return base64_qr

@app.route("/", methods=["GET", "POST"])
def index():
    data = load_data()

    if request.method == "POST":
        property_name = request.form.get("property_name")
        destination_url = request.form.get("destination_url")

        if not property_name or not destination_url:
            return render_template("index.html", error="Both fields are required!")

        if property_name in data:
            short_url = data[property_name]["short_url"]
            data[property_name]["destination_url"] = destination_url
        else:
            short_url = generate_short_url(property_name)
            qr_code_base64 = generate_qr_code_base64(short_url)
            data[property_name] = {
                "short_url": short_url,
                "destination_url": destination_url,
                "qr_code_base64": qr_code_base64
            }

        save_data(data)
        return render_template("index.html", short_url=short_url, qr_code_base64=data[property_name]["qr_code_base64"], public_url=PUBLIC_URL)

    return render_template("index.html")

@app.route("/<short_url>")
def redirect_url(short_url):
    data = load_data()
    for details in data.values():
        if details["short_url"] == short_url:
            return redirect(details["destination_url"])
    return "Short URL not found", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
"""

from flask import Flask, request, render_template, redirect
import json
import hashlib
import pyqrcode
import base64
import io
import os
import subprocess

app = Flask(__name__)

# 🔹 Secure GitHub Configuration (Using Environment Variables)
GITHUB_USERNAME = "Pavan-Eco-Retrofit"
GITHUB_TOKEN =   "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" # Get token from Render environment variables
GIT_REPO = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/Pavan-Eco-Retrofit/json_saving.git"

DATA_DIR = "data"
DATA_FILE = f"{DATA_DIR}/short_links.json"
PUBLIC_URL = "https://qrcode-fw9c.onrender.com/"  # Replace with your Render domain

# Ensure Data Directory Exists
os.makedirs(DATA_DIR, exist_ok=True)

# 🔹 Pull latest data from GitHub
def pull_data_from_git():
    if not os.path.exists(f"{DATA_DIR}/.git"):
        subprocess.run(["git", "clone", GIT_REPO, DATA_DIR], check=True)
    else:
        subprocess.run(["git", "-C", DATA_DIR, "fetch"], check=True)
        subprocess.run(["git", "-C", DATA_DIR, "reset", "--hard", "origin/main"], check=True)

# 🔹 Push new data to GitHub
def push_data_to_git():
    try:
        # Set Git user identity
        subprocess.run(["git", "-C", DATA_DIR, "config", "user.email", "pavan.banavasi@designspecifics.co.uk"], check=True)
        subprocess.run(["git", "-C", DATA_DIR, "config", "user.name", "Pavan-Eco-Retrofit"], check=True)

        # Add and commit changes
        subprocess.run(["git", "-C", DATA_DIR, "add", "short_links.json"], check=True)
        subprocess.run(["git", "-C", DATA_DIR, "commit", "-m", "Update short links"], check=True)
        subprocess.run(["git", "-C", DATA_DIR, "push", "origin", "main"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git Push Error: {e}")

# 🔹 Load Short Links Data from JSON (Ensures data is always pulled from GitHub)
def load_data():
    pull_data_from_git()  # Always fetch latest data before loading
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

# 🔹 Save Data to JSON & Push to GitHub
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
    push_data_to_git()  # Ensure data is committed & pushed to GitHub

# 🔹 Generate Short URL
def generate_short_url(property_name):
    return hashlib.md5(property_name.encode()).hexdigest()[:6]

# 🔹 Generate QR Code in Base64 (No File Storage Needed)
def generate_qr_code_base64(short_url):
    qr = pyqrcode.create(f"{PUBLIC_URL}{short_url}")
    buffer = io.BytesIO()
    qr.png(buffer, scale=6)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# 🔹 Homepage - Create Short URL & QR Code
@app.route("/", methods=["GET", "POST"])
def index():
    data = load_data()

    if request.method == "POST":
        property_name = request.form.get("property_name")
        destination_url = request.form.get("destination_url")

        if not property_name or not destination_url:
            return render_template("index.html", error="Both fields are required!")

        if property_name in data:
            short_url = data[property_name]["short_url"]
            data[property_name]["destination_url"] = destination_url
        else:
            short_url = generate_short_url(property_name)
            qr_code_base64 = generate_qr_code_base64(short_url)
            data[property_name] = {
                "short_url": short_url,
                "destination_url": destination_url,
                "qr_code_base64": qr_code_base64
            }

        save_data(data)
        return render_template("index.html", short_url=short_url, qr_code_base64=data[property_name]["qr_code_base64"], public_url=PUBLIC_URL)

    return render_template("index.html")

# 🔹 Redirect to Original URL
@app.route("/<short_url>")
def redirect_url(short_url):
    data = load_data()
    for details in data.values():
        if details["short_url"] == short_url:
            return redirect(details["destination_url"])
    return "Short URL not found", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
