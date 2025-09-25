from . import db
from flask_login import UserMixin
from datetime import datetime

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    rpps = db.Column(db.String(50), unique=True, nullable=False)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    specialite = db.Column(db.String(100))
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20))
    question_secrete = db.Column(db.String(200))
    reponse_secrete_hash = db.Column(db.String(200))

    # Relation avec les patients
    patients = db.relationship('Patient', backref='admin', lazy=True)


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    groupe_sanguin = db.Column(db.Enum('A+','A-','B+','B-','AB+','AB-','O+','O-', name='groupe_enum'))
    allergies = db.Column(db.String(200))
    contact_urgence = db.Column(db.String(50))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)  # peut être None

    # Relation avec les documents
    documents = db.relationship('Document', backref='patient', lazy=True)


class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    type = db.Column(db.String(50))
    file_path = db.Column(db.String(200))
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
