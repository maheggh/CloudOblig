from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import os
import certifi
import shutil
import tarfile
from markdown2 import markdown
from weasyprint import HTML

# Initialize FastAPI app
app = FastAPI()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]
contacts_collection = db["contacts"]

# Directories setup
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Ensure the file is a .tar.gz
    if not file.filename.endswith('.tar.gz'):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # Save the uploaded tar.gz file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Process the file
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=PROCESSED_FOLDER)
    
    # Implement processing logic (CSV parsing, Markdown conversion, PDF generation)
    # You need to create or integrate this functionality

    # Re-compress the processed files into a new tar.gz
    processed_file_path = os.path.join(PROCESSED_FOLDER, "processed.tar.gz")
    with tarfile.open(processed_file_path, "w:gz") as tar:
        tar.add(PROCESSED_FOLDER, arcname=".")

    # Serve the processed file for download
    return FileResponse(processed_file_path, media_type='application/gzip', filename='processed.tar.gz')

@app.get("/download/{filename}")
async def download(filename: str):
    # Serve the processed file for download
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='application/gzip', filename=filename)
    raise HTTPException(status_code=404, detail="File not found.")

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    # Run the application
    # You will need an ASGI server like Uvicorn to run this app
    # Use the command: `uvicorn main:app --host 0.0.0.0 --port 8000`
    pass
