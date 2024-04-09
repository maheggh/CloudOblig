from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import csv
import aiofiles
import zipfile
from uuid import uuid4

# Initialize the FastAPI app
app = FastAPI()

# Define folder paths
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
ZIP_FOLDER = 'zip_files'
TEMP_FOLDER = 'temp_files'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Async function to process the CSV using the markdown template
async def process_csv(csv_file_path: str, template_content: str, file_id: str) -> str:
    processed_files = []
    async with aiofiles.open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        content = await csvfile.read()
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            first_name = row.get('FirstName', '')
            last_name = row.get('LastName', '')
            if first_name and last_name:
                md_filename = f"{first_name}_{last_name}.md"
                md_file_path = os.path.join(PROCESSED_FOLDER, md_filename)
                markdown_content = template_content.format(**row)
                async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                    await md_file.write(markdown_content)
                processed_files.append(md_file_path)
    
    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
    
    # Clean up processed markdown files
    for file in processed_files:
        os.remove(file)
    
    return zip_file_path

# Endpoint to upload a zip file
@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    file_id = str(uuid4())
    zip_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.zip")
    
    async with aiofiles.open(zip_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    template_content = ""
    csv_file_path = ""
    
    # Extract the zip file and find the CSV and template files
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(TEMP_FOLDER)
        for file_name in zipf.namelist():
            if file_name.endswith('.md'):
                template_path = os.path.join(TEMP_FOLDER, file_name)
                async with aiofiles.open(template_path, 'r') as template_file:
                    template_content = await template_file.read()
            elif file_name.endswith('.csv'):
                csv_file_path = os.path.join(TEMP_FOLDER, file_name)
    
    if not template_content or not csv_file_path:
        raise HTTPException(status_code=400, detail="ZIP does not contain both .md and .csv files.")
    
    # Process the CSV file with the template content
    zip_file_path = await process_csv(csv_file_path, template_content, file_id)
    
    # Clean up temp directory
    os.remove(zip_path)
    os.remove(template_path)
    os.remove(csv_file_path)
    
    # Return the ID for the zip file for downloading
    return {"file_id": file_id}

# Endpoint to download the processed zip file
@app.get("/download-zip/{file_id}")
async def download_zip(file_id: str):
    zip_file_path = os.path.join(ZIP_FOLDER, f"{file_id}.zip")
    if os.path.exists(zip_file_path):
        return FileResponse(
            path=zip_file_path, 
            media_type='application/zip', 
            filename="output.zip"  # This sets the filename for the download
        )
    raise HTTPException(status_code=404, detail="File not found")

# Mount static files directory
app.mount("/", StaticFiles(directory="static", html=True), name="static")
