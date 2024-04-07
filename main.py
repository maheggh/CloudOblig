import os
import csv
import aiofiles
import zipfile
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
ZIP_FOLDER = 'zip_files'
STATIC_IMAGES_FOLDER = 'static/images'  # Assuming this is your static images path

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
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as csvfile:
        csv_content = await csvfile.read()
    
    reader = csv.DictReader(csv_content.splitlines())
    for row in reader:
        first_name = row.get('FirstName', '').strip()
        last_name = row.get('LastName', '').strip()
        if first_name and last_name:
            md_filename = f"{first_name}_{last_name}.md"
            md_file_path = os.path.join(PROCESSED_FOLDER, md_filename)
            markdown_content = template_content.format(**row)
            with open(md_file_path, 'w', encoding='utf-8') as md_file:
                md_file.write(markdown_content)
            processed_files.append(md_file_path)

    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
        # Add specific images to the ZIP
        images_to_include = ['ntnu-logo.jpg', 'signature.png']
        add_images_to_zip(zipf, STATIC_IMAGES_FOLDER, images_to_include)

    return zip_file_path
