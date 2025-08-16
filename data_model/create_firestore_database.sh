#!/bin/bash
# This script creates a new Firestore database.

# Set the database ID and location
DATABASE_ID="agro_extension_db"
LOCATION="us-central1"

# Create the Firestore database
echo "Creating Firestore database '${DATABASE_ID}' in location '${LOCATION}'...
"
gcloud firestore databases create --database=${DATABASE_ID} --location=${LOCATION}
