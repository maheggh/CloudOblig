from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import aiofiles
from werkzeug.utils import secure_filename
import shutil

# Import the process_csv function from the csvhandling module
from csvhandling import process_csv as process_csv_flask

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a zip file.")

    zip_filename = secure_filename(file.filename)
    zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)

    async with aiofiles.open(zip_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Process CSV using csvhandling script
    output_zip_path = await process_csv(zip_path)

    if not os.path.exists(output_zip_path):
        raise HTTPException(status_code=500, detail="Error processing CSV.")

    return FileResponse(output_zip_path, media_type='application/zip', filename='processed_files.zip')

@app.get("/processed_file")
async def download_processed_file():
    processed_file_path = os.path.join(OUTPUT_FOLDER, 'output.zip')
    if os.path.exists(processed_file_path):
        return FileResponse(processed_file_path, media_type='application/zip', filename='output.zip')
    raise HTTPException(status_code=404, detail="Processed file not found")

def process_csv(zip_path):
    # Extract CSV and template file from the ZIP
    # You need to implement this logic based on your file structure

    # For now, let's assume you have the paths to the CSV and template file
    csv_file = "path_to_csv_file.csv"
    template_file = "path_to_template_file.md"

    # Process CSV using csvhandling script
    return process_csv_flask(csv_file, template_file)

app.mount("/", StaticFiles(directory="static", html=True), name="static")