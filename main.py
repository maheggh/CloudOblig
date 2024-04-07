from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import os
import certifi
import csv
import aiofiles

app = FastAPI()

# MongoDB setup using environment variables for security
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]
contacts_collection = db["contacts"]

UPLOAD_FOLDER = 'assets'
PROCESSED_FOLDER = 'processed_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

template_content = """
# Certificate of excellence
![NTNU-logo](/static/images/NTNU-logo.png)
{FirstName} {LastName} have completed the course IDG2001 Cloud Technologies at
(NTNU). As part of their course, they have blabla skills, lists, etc.
- SaaS, PaaS, IaaS
- Cloud infrastructure ... etc
![Signature](/static/images/signature.png)
Paul Knutson, Faculty of IE, NTNU
"""

async def insert_contacts_to_db(reader, db_collection):
    for row in reader:
        db_collection.insert_one(row)

async def generate_markdown_files(csv_file_path: str, output_dir: str):
    async with aiofiles.open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(await csvfile.read().splitlines())
        
        # Inserting CSV data into MongoDB
        await insert_contacts_to_db(reader, contacts_collection)
        
        for row in reader:
            # You should replace placeholders here
            markdown_content = template_content.format(**row)
            md_filename = f"{row['FirstName']}_{row['LastName']}.md"
            md_file_path = os.path.join(output_dir, md_filename)
            async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                await md_file.write(markdown_content)

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if file.filename.endswith('.csv'):
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        async with aiofiles.open(file_location, "wb+") as file_object:
            content = await file.read()
            await file_object.write(content)
            
        # Process the CSV file to create Markdown files and insert data into MongoDB
        await generate_markdown_files(file_location, PROCESSED_FOLDER)
        
        return {"message": "CSV processed, Markdown files created, and data inserted into MongoDB."}
    raise HTTPException(status_code=400, detail="Invalid file extension.")

# The download endpoint remains unchanged...


# Assume that the Markdown files have been converted to HTML or PDF and saved in PROCESSED_FOLDER
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)
    raise HTTPException(status_code=404, detail="File not found.")