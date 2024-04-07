from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import os
import certifi
import csv
import aiofiles
import shutil
from starlette.responses import Response

# Initialize FastAPI app
app = FastAPI()

# MongoDB setup using environment variables for security
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]  # Use the test database
contacts_collection = db["contacts"]  # Use the contacts collection

# Directories setup
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
os.makedirs(PROCESSED_FOLDER, exist_ok=True)  # Ensure the processed folder exists

# Template content (would normally be loaded from a file)
template_content = """
# Certificate of excellence
![NTNU-logo](NTNU-logo.png)
{{FirstName}} {{LastName}} have completed the course IDG2001 Cloud Technologies at
(NTNU). As part of their course, they have blabla skills, lists, etc.
- SaaS, PaaS, IaaS
- Cloud infrastructure ... etc
![Signature](signature.png)
Paul Knutson, Faculty of IE, NTNU
"""

async def generate_markdown_files(csv_file_path: str, output_dir: str):
    async with aiofiles.open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(await csvfile.read().splitlines())
    
        for row in reader:
            markdown_content = template_content.replace('{{FirstName}}', row['FirstName']).replace('{{LastName}}', row['LastName'])
            md_file_path = os.path.join(output_dir, f"{row['FirstName']}_{row['LastName']}.md")
            async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                await md_file.write(markdown_content)
    return [os.path.join(output_dir, f"{row['FirstName']}_{row['LastName']}.md") for row in reader]

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        async with aiofiles.open(file_location, "wb+") as file_object:
            content = await file.read()
            await file_object.write(content)

        markdown_files = await generate_markdown_files(file_location, PROCESSED_FOLDER)
        return {"message": "CSV processed and Markdown files created.", "files": markdown_files}
    raise HTTPException(status_code=400, detail="Invalid file extension.")

@app.get("/download-md/{filename}")
async def download_md(filename: str):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='text/markdown', filename=filename)
    raise HTTPException(status_code=404, detail="File not found.")

# Serve static files (e.g., index.html, CSS, JavaScript)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
