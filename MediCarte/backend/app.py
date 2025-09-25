# app.py
from medcard import create_app, db
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Créer l'application via la factory
app = create_app()

# Créer la base de données si elle n'existe pas
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Démarrer le serveur en mode debug si besoin
    app.run(debug=True)
