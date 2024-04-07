import csv
import os
from pymongo import MongoClient
import certifi

def import_contacts_from_csv(csv_path: str, mongodb_uri: str, db_name: str, collection_name: str):
    """
    Imports contacts from a CSV file into the MongoDB collection.

    :param csv_path: Path to the CSV file containing contacts.
    :param mongodb_uri: MongoDB connection URI.
    :param db_name: Name of the database.
    :param collection_name: Name of the collection.
    """
    client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
    db = client[db_name]
    contacts_collection = db[collection_name]

    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for contact in reader:
            # Simplify the document structure if possible
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
    # Example usage
    MONGODB_URI = os.getenv('MONGODB_URI', 'your_default_mongodb_uri_here')
    DB_NAME = "test"
    COLLECTION_NAME = "contacts"
    # Define the CSV file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, 'assets')  
    csv_path = os.path.join(assets_dir, 'personas.csv')  
    
    import_contacts_from_csv(csv_path, MONGODB_URI, DB_NAME, COLLECTION_NAME)
    print("Contacts imported successfully.")