from pymongo import MongoClient
import gridfs

# Asegúrate que el puerto y host estén correctos
client = MongoClient("mongodb://localhost:27017")
db = client["classroom_db"]
fs = gridfs.GridFS(db)
