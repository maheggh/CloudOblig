import csv
import os
from pymongo import MongoClient
import certifi

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI', 'your_default_mongodb_uri_here')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client["test"]
contacts_collection = db["contacts"]  

script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, 'assets')  
csv_path = os.path.join(assets_dir, 'personas.csv')  

def import_contacts_from_csv(csv_path: str):
    """
    Imports contacts from a CSV file into the MongoDB collection.

    :param csv_path: Path to the CSV file containing contacts.
    """
    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        contacts = [contact for contact in reader] 
        
        for contact in contacts:
            contact_document = {
                "email": contact.get("Email", "").strip(),
                "name": f"{contact.get('FirstName', '').strip()} {contact.get('LastName', '').strip()}",
                "phone": contact.get("Phone", "--No Information--").strip(),
                "address": contact.get("Address", "--No Information--").strip(),
                "company": contact.get("Company", "--No Information--").strip()
            }
            result = contacts_collection.insert_one(contact_document)
            print(f"Inserted: {result.inserted_id}")

if __name__ == "__main__":
    import_contacts_from_csv(csv_path)
    print("Contacts imported successfully.")
