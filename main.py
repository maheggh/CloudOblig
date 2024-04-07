from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import csv
import aiofiles
import zipfile
from uuid import uuid4

app = FastAPI()

UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
ZIP_FOLDER = 'zip_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)

template_content = """
# Certificate of Excellence

![NTNU Logo](ntnu-logo.jpg)

**{{FirstName}} {{LastName}}** have completed the course IDG2001 Cloud Technologies at the Norwegian University of Science and Technology (NTNU). As part of their course, they have demonstrated outstanding skills in Cloud Technologies, including PaaS, SaaS, and IaaS.

- PaaS: Platform as a Service
- SaaS: Software as a Service
- IaaS: Infrastructure as a Service

![Signature](signature.png)

_Paul Knutson, Faculty of IE, NTNU_
"""

async def process_csv(file_path: str, file_id: str) -> str:
    processed_files = []
    # Read the CSV file content asynchronously
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as csvfile:
        csv_content = await csvfile.read()

    # Process the CSV content synchronously
    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        first_name = row.get('FirstName', '').strip()
        last_name = row.get('LastName', '').strip()
        if first_name and last_name:  # Ensure non-empty names
            md_filename = f"{first_name}_{last_name}.md"
            md_file_path = os.path.join(PROCESSED_FOLDER, md_filename)
            markdown_content = template_content.format(**row)
            # Write the markdown content synchronously for simplicity
            with open(md_file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)
            processed_files.append(md_file_path)
            print(f"Processed: {md_file_path}")  # Debugging

    # Ensure the ZIP file creation and file addition happen correctly
    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
        # Add specific images to the ZIP
        images_to_include = ['ntnu-logo.jpg', 'signature.png']
        for image in images_to_include:
            image_path = os.path.join('static/images', image)  # Adjust as needed
            zipf.write(image_path, arcname=os.path.join('images', image))  # Adjust the arcname as per your directory structure in ZIP

    return zip_file_path


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.csv")
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Process the CSV file and create a ZIP archive
    zip_file_path = await process_csv(file_path, file_id)
    
    # Return the ID for the zip file for downloading
    return {"file_id": file_id}

@app.get("/download-zip/{file_id}")
async def download_zip(file_id: str):
    zip_file_path = os.path.join(ZIP_FOLDER, f"{file_id}.zip")
    if os.path.exists(zip_file_path):
        return FileResponse(zip_file_path, media_type='application/zip', filename=f"{file_id}.zip")
    raise HTTPException(status_code=404, detail="File not found")

app.mount("/", StaticFiles(directory="static", html=True), name="static")
