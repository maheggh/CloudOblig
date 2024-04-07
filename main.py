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

def add_images_to_zip(zipf, image_directory, images):
    for image in images:
        image_path = os.path.join(image_directory, image)
        if os.path.exists(image_path):
            zipf.write(image_path, arcname=image)
        else:
            print(f"Warning: Image not found at {image_path}")

async def process_csv(file_path: str, file_id: str) -> str:
    processed_files = []
    # Your existing logic to create and add .md files to processed_files
    
    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
        # Add images to ZIP
        images_to_include = ['ntnu-logo.jpg', 'signature.png']
        add_images_to_zip(zipf, 'static/images', images_to_include)

    # Your existing cleanup logic
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
