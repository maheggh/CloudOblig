from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi
import csv
import aiofiles

load_dotenv()

app = FastAPI()

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]  # Adjust as needed
contacts_collection = db["test"]  # Adjust as needed

UPLOAD_FOLDER = 'assets'
PROCESSED_FOLDER = 'processed_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

template_content = """
# Certificate of excellence
![NTNU-logo](NTNU-logo.png)
{FirstName} {LastName} have completed the course IDG2001 Cloud Technologies at
(NTNU). As part of their course, they have blabla skills, lists, etc.
- SaaS, PaaS, IaaS
- Cloud infrastructure ... etc
![Signature](signature.png)
Paul Knutson, Faculty of IE, NTNU
"""

async def generate_markdown_files_and_insert_to_db(csv_file_path: str, output_dir: str, db_collection):
    async with aiofiles.open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        content = await csvfile.read()
        reader = csv.DictReader(content.splitlines())
        
        # Reset the list for generated files
        generated_files = []
        
        for row in reader:
            # Insert contact into MongoDB
            db_collection.insert_one(row)
            
            # Generate Markdown content
            markdown_content = template_content.format(**row)
            md_filename = f"{row['FirstName']}_{row['LastName']}.md"
            md_file_path = os.path.join(output_dir, md_filename)
            async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                await md_file.write(markdown_content)
            
            # Keep track of generated files
            generated_files.append(md_file_path)
            
        return generated_files

@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    async with aiofiles.open(file_location, "wb+") as file_object:
        content = await file.read()
        await file_object.write(content)
    
    generated_files = await generate_markdown_files_and_insert_to_db(file_location, PROCESSED_FOLDER, contacts_collection)
    
    # For simplicity, return the first processed file or adjust as needed
    if generated_files:
        return FileResponse(path=generated_files[0], filename=os.path.basename(generated_files[0]), media_type='text/markdown')
    else:
        return {"message": "No files processed."}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
