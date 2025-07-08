from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

import os
load_dotenv() 
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["surakshak"]

async def save_analysis(result: dict):
    await db["analyses"].insert_one(result)

async def get_recent_logs(limit=10):
    cursor = db["analyses"].find().sort("_id", -1).limit(limit)
    return await cursor.to_list(length=limit)


