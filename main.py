from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import csv
import aiofiles
import zipfile
from uuid import uuid4
import shutil

app = FastAPI()

UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
ZIP_FOLDER = 'zip_files'
TEMP_FOLDER = 'temp_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(TEMP_FOLDER),
    autoescape=select_autoescape()
)

async def process_csv_and_template(csv_file_path: str, template_name: str, file_id: str) -> str:
    processed_files = []

    template = env.get_template(template_name)

    async with aiofiles.open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        content = await csvfile.read()
        reader = csv.DictReader(content.splitlines())

        for row in reader:
            md_filename = f"{row['FirstName']}_{row['LastName']}.md"
            md_file_path = os.path.join(PROCESSED_FOLDER, md_filename)
            markdown_content = template.render(row)

            async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                await md_file.write(markdown_content)
            processed_files.append(md_file_path)

    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in processed_files:
            zipf.write(file_path, os.path.basename(file_path))

    return zip_file_path

@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    file_id = str(uuid4())
    zip_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.zip")

    async with aiofiles.open(zip_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(TEMP_FOLDER)
        template_name = ""
        csv_file_path = ""
        for file_name in zipf.namelist():
            if file_name.endswith('.md'):
                template_name = file_name
            elif file_name.endswith('.csv'):
                csv_file_path = os.path.join(TEMP_FOLDER, file_name)
    
    zip_file_path = await process_csv_and_template(csv_file_path, template_name, file_id)

    shutil.rmtree(TEMP_FOLDER, ignore_errors=True)

    return {"file_id": file_id}

@app.get("/download-zip/{file_id}")
async def download_zip(file_id: str):
    zip_file_path = os.path.join(ZIP_FOLDER, f"{file_id}.zip")
    if os.path.exists(zip_file_path):
        return FileResponse(path=zip_file_path, media_type='application/zip', filename="output.zip")
    raise HTTPException(status_code=404, detail="File not found")

app.mount("/", StaticFiles(directory="static", html=True), name="static")
