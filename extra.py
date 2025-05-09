import pymongo
import os
from dotenv import load_dotenv

# Load .env if used
load_dotenv()

# Your Mongo URI
MONGO_DB_URL = os.getenv("MONGO_DB_URL")  # or directly use string

client = pymongo.MongoClient(MONGO_DB_URL)

# List all databases
print("📂 Available Databases:")
print(client.list_database_names())

# Check if SamAi exists
db = client.get_database("SamAi")
print("\n📁 Collections in 'SamAi':")
print(db.list_collection_names())

# Check if NetworkData has documents
collection = db.get_collection("NetworkData")
print("\n🔍 First 5 documents in 'NetworkData':")
for doc in collection.find().limit(5):
    print(doc)
