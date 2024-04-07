from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import os
import certifi
import csv
import aiofiles

# Initialize FastAPI app
app = FastAPI()

# MongoDB setup using environment variables for security
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]
contacts_collection = db["contacts"]

# Directories setup
UPLOAD_FOLDER = 'assets'
PROCESSED_FOLDER = 'processed_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Serve static files including index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# The template content should be moved into an actual .md file inside 'assets' if it is static
# Or generated dynamically within this function if it changes
template_content = """
# Certificate of excellence
![NTNU-logo](/static/images/NTNU-logo.png)
{{FirstName}} {{LastName}} have completed the course IDG2001 Cloud Technologies at
(NTNU). As part of their course, they have blabla skills, lists, etc.
- SaaS, PaaS, IaaS
- Cloud infrastructure ... etc
![Signature](/static/images/signature.png)
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

        await generate_markdown_files(file_location, PROCESSED_FOLDER)
        return {"message": "CSV processed and Markdown files created."}
    raise HTTPException(status_code=400, detail="Invalid file extension.")

# Assume that the Markdown files have been converted to HTML or PDF and saved in PROCESSED_FOLDER
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)
    raise HTTPException(status_code=404, detail="File not found.")