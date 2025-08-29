from google.cloud import firestore

def list_collections(project_id):
    db = firestore.Client(project=project_id, database='agro-extension-db')
    for collection in db.collections():
        print(f"Collection ID: {collection.id}")

if __name__ == "__main__":
    list_collections("agro-extension-digital-npe")