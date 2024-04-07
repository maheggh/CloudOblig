from flask import Flask, request, jsonify, render_template, Response
from werkzeug.utils import secure_filename
import os
import pymongo
import certifi
from bson import json_util
import csv

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup using environment variables for security
MONGODB_URI = os.getenv('MONGODB_URI', 'default_mongodb_uri_if_not_set')
client = pymongo.MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]  # Use the test database
contacts_collection = db["contacts"]  # Use the contacts collection

# Directories setup
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and secure_filename(file.filename).endswith('.csv'):
            filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            file.save(filepath)
            
            # Process CSV file
            with open(filepath, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    # Assuming your CSV has columns that match the MongoDB document structure
                    contacts_collection.insert_one(row)
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify({"message": "CSV processed and data inserted into MongoDB."})
        else:
            return jsonify({"error": "Only CSV files are allowed."}), 400
    else:
        # Show the upload form for GET requests
        return render_template('index.html')

@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = list(contacts_collection.find({}, {'_id': False}))  # Exclude the MongoDB id from the results
    return jsonify(contacts)

if __name__ == '__main__':
    app.run(debug=True, port=6438)
