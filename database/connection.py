import motor.motor_asyncio
# from decouple import config
import certifi
import os

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

print("DEBUG MONGO_URL:", os.getenv("MONGODB_URL"))
print("DEBUG DB_NAME:", os.getenv("DATABASE_NAME"))


# Use certifi to fix SSL certificate verification
client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL,
    tlsCAFile=certifi.where()
)

database = client[DATABASE_NAME]

# Collections
user_collection = database.get_collection("users")
template_collection = database.get_collection("templates")
saved_templates_collection = database.get_collection("saved_templates")
project_collection = database.get_collection("projects")
