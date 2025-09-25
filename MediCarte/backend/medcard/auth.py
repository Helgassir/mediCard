# medcard/auth.py
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Admin
from . import db

# --- Gestion des mots de passe ---
def set_password(password: str) -> str:
    """Génère un hash sécurisé du mot de passe."""
    return generate_password_hash(password, method="pbkdf2:sha256")  

def check_password(user: Admin, password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash."""
    return check_password_hash(user.password_hash, password)

# --- Gestion de la réponse secrète ---
def set_reponse_secrete_hash(reponse: str) -> str:
    """Hash la réponse secrète."""
    return generate_password_hash(reponse, method="pbkdf2:sha256")

def check_reponse_secrete_hash(user: Admin, reponse: str) -> bool:
    """Vérifie si la réponse secrète correspond au hash stocké."""
    return check_password_hash(user.reponse_secrete_hash, reponse)

# --- Gestion des utilisateurs ---
def create_admin(rpps: str, password: str, role: str, question: str, reponse: str, nom=None, prenom=None, specialite=None):
    """
    Créer un nouvel admin/médecin dans la base de données.
    Les champs nom, prenom et spécialité sont optionnels.
    """
    password_hash = set_password(password)
    reponse_secrete_hash = set_reponse_secrete_hash(reponse)

    new_admin = Admin(
        rpps=rpps,
        password_hash=password_hash,
        role=role,
        question_secrete=question,
        reponse_secrete_hash=reponse_secrete_hash,
        nom=nom,
        prenom=prenom,
        specialite=specialite
    )
    db.session.add(new_admin)
    db.session.commit()
    return new_admin

# --- Réinitialisation du mot de passe via question secrète ---
def reset_password_with_secret(user: Admin, reponse: str, new_password: str) -> bool:
    """
    Réinitialise le mot de passe si la réponse à la question secrète est correcte.
    Retourne True si succès, False sinon.
    """
    if check_reponse_secrete_hash(user, reponse):
        user.password_hash = set_password(new_password)
        db.session.commit()
        return True
    return False
