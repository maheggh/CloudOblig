from fastapi import FastAPI, File, UploadFile, HTTPException
from pymongo import MongoClient
import os
import certifi
import csv
from starlette.responses import JSONResponse
import aiofiles  # You need to install this package for async file operations

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

async def process_csv_file(file_path: str, contacts_collection):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as csvfile:
        # Since aiofiles doesn't support csv.DictReader directly,
        # read the file content asynchronously, then use csv.DictReader on the content.
        content = await csvfile.read()
    reader = csv.DictReader(content.splitlines())
    
    for row in reader:
        # Transform and insert each contact into the MongoDB collection
        contact_document = {
            "email": row.get("Email", "").strip(),
            "name": f"{row.get('FirstName', '').strip()} {row.get('LastName', '').strip()}",
            "phone": row.get("Phone", "--No Information--").strip(),
            "address": row.get("Address", "--No Information--").strip(),
            "company": row.get("Company", "--No Information--").strip()
        }
        contacts_collection.insert_one(contact_document)

@app.post('/upload-csv/')
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File extension not allowed.")
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    async with aiofiles.open(file_location, "wb+") as file_object:
        # Read content from UploadFile and write it asynchronously
        content = await file.read()
        await file_object.write(content)
    
    # Process the CSV file
    await process_csv_file(file_location, contacts_collection)
    os.remove(file_location)  # Clean up the uploaded file
    return {"message": "CSV processed and data inserted into MongoDB."}

@app.get('/contacts/')
async def get_contacts():
    contacts = list(contacts_collection.find({}, {'_id': False}))  # Exclude the MongoDB id from the results
    return contacts
