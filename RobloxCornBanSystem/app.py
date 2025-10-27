from flask import Flask, jsonify, request
from pymongo import MongoClient
import os # 👈 Wichtig: Für das Lesen von Umgebungsvariablen

# ⚠️ ALLE VARIABLEN WERDEN NUN AUS DER RENDER-UMGEBUNG GELESEN ⚠️
# Stelle sicher, dass diese Variablen in deinem Render Dashboard gesetzt sind!

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
AUTH_KEY = os.environ.get("AUTH_KEY")

# Flask-App initialisieren (Wird von Gunicorn gefunden)
app = Flask(__name__)

# Datenbankverbindung herstellen
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("MongoDB connection established successfully.")
except Exception as e:
    # Bei einem Fehler die Anwendung NICHT starten (wird aber meistens durch Gunicorn abgefangen)
    print(f"ERROR: Could not connect to MongoDB. Check MONGO_URI and Network Access. Details: {e}")

@app.route('/get_ban_list', methods=['GET'])
def get_ban_list():
    # 1. Sicherheit: Prüfe den API-Schlüssel
    auth_header = request.headers.get('Authorization')
    
    # Überprüfen, ob AUTH_KEY in Render gesetzt wurde
    if not AUTH_KEY:
        return jsonify({"status": "error", "message": "API key is not configured on the server."}), 500

    if not auth_header or auth_header != f"Bearer {AUTH_KEY}":
        # 401 Unauthorized, wenn der Schlüssel fehlt oder falsch ist
        return jsonify({"status": "error", "message": "Unauthorized access."}), 401

    try:
        # 2. Daten von MongoDB abrufen
        # Wir holen alle Dokumente, projizieren (zeigen) nur das Feld "userId"
        cursor = collection.find({}, {"userId": 1, "_id": 0})
        
        # 3. Nur die IDs in eine Liste umwandeln
        user_ids = [doc['userId'] for doc in cursor]
        
        # 4. JSON-Antwort an Roblox senden
        return jsonify({
            "status": "success",
            "user_ids": user_ids
        }), 200

    except Exception as e:
        # 500 Internal Server Error, falls etwas schiefgeht
        print(f"Database error during query: {e}")
        return jsonify({"status": "error", "message": "Internal server error during query."}), 500

# ⚠️ WICHTIG: Der if __name__ == '__main__': Block MUSS FÜR RENDER ENTFERNT WERDEN!
# Gunicorn übernimmt den Startbefehl.
