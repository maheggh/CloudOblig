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
Congratulations {FirstName} {LastName} on completing the course!

As part of the course IDG2001 Cloud Technologies at NTNU, you demonstrated great skill and knowledge.
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
            print(f"Added to ZIP: {file}")  # Debugging

    # Optional: Comment out for debugging
    # for file in processed_files:
    #     os.remove(file)

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
