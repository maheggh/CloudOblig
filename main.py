from fastapi import FastAPI, File, UploadFile
from pymongo import MongoClient
import os
import certifi
import csv
from starlette.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI()

# MongoDB setup using environment variables for security
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]  # Use the test database
contacts_collection = db["contacts"]  # Use the contacts collection

# Directories setup
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

@app.post('/upload-csv/')
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return JSONResponse(status_code=400, content={"message": "File extension not allowed."})
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Process CSV file
    with open(file_location, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Assuming your CSV has columns that match the MongoDB document structure
            contacts_collection.insert_one(row)
    os.remove(file_location)  # Clean up the uploaded file
    return {"message": "CSV processed and data inserted into MongoDB."}

@app.get('/contacts/')
async def get_contacts():
    contacts = list(contacts_collection.find({}, {'_id': False}))  # Exclude the MongoDB id from the results
    return contacts
