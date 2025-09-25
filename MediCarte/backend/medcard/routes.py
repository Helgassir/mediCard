import os
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import Admin, Patient
from .auth import check_password, check_reponse_secrete_hash, create_admin, set_password

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def init_routes(app):

    # --- INDEX ---
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    # --- LOGIN ---
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            rpps = request.form.get('rpps')
            password = request.form.get('password')
            user = Admin.query.filter_by(rpps=rpps).first()
            if user and check_password(user, password):
                login_user(user)
                flash("Connexion réussie ✅", "success")
                if user.role == "admin":
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard_patients'))
            flash("❌ RPPS ou mot de passe incorrect", "danger")
        return render_template('login.html')

    # --- LOGOUT ---
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("Vous êtes déconnecté ✅", "info")
        return redirect(url_for('login'))

    # --- SIGNUP ---
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            rpps = request.form['rpps']
            password = request.form['password']
            role = request.form['role']
            question = request.form['question_secrete']
            reponse = request.form['reponse_secrete']
            nom = request.form.get('nom')
            prenom = request.form.get('prenom')
            specialite = request.form.get('specialite')

            if Admin.query.filter_by(rpps=rpps).first():
                flash("⚠️ RPPS déjà utilisé", "warning")
                return redirect(url_for('signup'))

            create_admin(rpps, password, role, question, reponse, nom, prenom, specialite)
            flash("✅ Compte créé avec succès, vous pouvez vous connecter", "success")
            return redirect(url_for('login'))

        return render_template('signup.html')

    # --- DASHBOARD ADMIN ---
    @app.route('/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != "admin":
            flash("❌ Accès réservé aux administrateurs", "danger")
            return redirect(url_for('logout'))
        return render_template('dashboard.html')  # choix : gérer médecins ou patients

    # --- DASHBOARD MEDECIN / PATIENTS ---
    @app.route('/dashboard_medecin')
    @login_required
    def dashboard_patients():
        if current_user.role not in ["medecin", "admin"]:
            flash("❌ Accès interdit", "danger")
            return redirect(url_for('logout'))

        if current_user.role == "medecin":
            patients = Patient.query.filter_by(admin_id=current_user.id).all()
        else:
            patients = Patient.query.all()

        medecins = Admin.query.filter_by(role="medecin").all() if current_user.role=="admin" else []
        return render_template('dashboard_medecin.html', patients=patients, medecins=medecins)

    # --- LISTE MEDECINS ---
    @app.route('/medecins')
    @login_required
    def medecins_list():
        if current_user.role != "admin":
            flash("❌ Accès réservé aux administrateurs", "danger")
            return redirect(url_for('logout'))
        medecins = Admin.query.filter_by(role="medecin").all()
        return render_template('medecin.html', medecins=medecins)

    # --- AJOUTER UN MEDECIN ---
    @app.route('/medecin/add', methods=['GET', 'POST'])
    @login_required
    def add_medecin():
        if current_user.role != "admin":
            flash("❌ Accès réservé aux administrateurs", "danger")
            return redirect(url_for('logout'))
        if request.method == 'POST':
            rpps = request.form['rpps']
            nom = request.form['nom']
            prenom = request.form['prenom']
            specialite = request.form.get('specialite') or "generaliste"
            password = request.form['password']
            reponse = request.form['reponse_secrete']

            if Admin.query.filter_by(rpps=rpps).first():
                flash("⚠️ RPPS déjà utilisé", "warning")
                return redirect(url_for('add_medecin'))

            create_admin(rpps, password, "medecin",
                         "Quel est le nom de votre école primaire ?", 
                         reponse, nom, prenom, specialite)
            flash("✅ Médecin ajouté avec succès", "success")
            return redirect(url_for('medecins_list'))
        return render_template('add_medecin.html')

    # --- MODIFIER UN MEDECIN ---
    @app.route('/medecin/edit/<int:medecin_id>', methods=['GET', 'POST'])
    @login_required
    def edit_medecin(medecin_id):
        if current_user.role != "admin":
            flash("❌ Accès réservé aux administrateurs", "danger")
            return redirect(url_for('logout'))
        medecin = Admin.query.get_or_404(medecin_id)
        if request.method == 'POST':
            medecin.nom = request.form['nom']
            medecin.prenom = request.form['prenom']
            medecin.specialite = request.form.get('specialite') or "generaliste"
            db.session.commit()
            flash("✅ Médecin modifié avec succès", "success")
            return redirect(url_for('medecins_list'))
        return render_template('edit_medecin.html', medecin=medecin)

    # --- SUPPRIMER UN MEDECIN ---
    @app.route('/medecin/delete/<int:medecin_id>')
    @login_required
    def delete_medecin(medecin_id):
        if current_user.role != "admin":
            flash("❌ Accès réservé aux administrateurs", "danger")
            return redirect(url_for('logout'))
        medecin = Admin.query.get_or_404(medecin_id)
        db.session.delete(medecin)
        db.session.commit()
        flash("✅ Médecin supprimé avec succès", "success")
        return redirect(url_for('medecins_list'))

    # --- AJOUTER UN PATIENT ---
    @app.route('/patient/add', methods=['GET', 'POST'])
    @login_required
    def add_patient():
        if current_user.role not in ["admin", "medecin"]:
            flash("❌ Accès interdit", "danger")
            return redirect(url_for('logout'))
        if request.method == 'POST':
            groupe_sanguin = request.form['groupe_sanguin']
            if groupe_sanguin == 'autre':
                groupe_sanguin = request.form.get('groupe_sanguin_autre')
            new_patient = Patient(
                nom=request.form['nom'],
                prenom=request.form['prenom'],
                groupe_sanguin=groupe_sanguin,
                allergies=request.form.get('allergies'),
                contact_urgence=request.form.get('contact_urgence'),
                admin_id=current_user.id if current_user.role=="medecin" else None
            )
            db.session.add(new_patient)
            db.session.commit()
            flash("✅ Patient ajouté avec succès", "success")
            return redirect(url_for('dashboard_patients'))
        return render_template('add_patient.html')

    # --- MODIFIER UN PATIENT ---
    @app.route('/patient/edit/<int:patient_id>', methods=['GET', 'POST'])
    @login_required
    def edit_patient(patient_id):
        patient = Patient.query.get_or_404(patient_id)
        if current_user.role=="medecin" and patient.admin_id != current_user.id:
            flash("❌ Accès interdit", "danger")
            return redirect(url_for('logout'))
        if request.method=='POST':
            groupe_sanguin = request.form['groupe_sanguin']
            if groupe_sanguin == 'autre':
                groupe_sanguin = request.form.get('groupe_sanguin_autre')
            patient.nom = request.form['nom']
            patient.prenom = request.form['prenom']
            patient.groupe_sanguin = groupe_sanguin
            patient.allergies = request.form.get('allergies')
            patient.contact_urgence = request.form.get('contact_urgence')
            db.session.commit()
            flash("✅ Patient modifié avec succès", "success")
            return redirect(url_for('dashboard_patients'))
        return render_template('edit_patient.html', patient=patient)

    # --- SUPPRIMER UN PATIENT ---
    @app.route('/patient/delete/<int:patient_id>')
    @login_required
    def delete_patient(patient_id):
        patient = Patient.query.get_or_404(patient_id)
        if current_user.role=="medecin" and patient.admin_id != current_user.id:
            flash("❌ Accès interdit", "danger")
            return redirect(url_for('logout'))
        db.session.delete(patient)
        db.session.commit()
        flash("✅ Patient supprimé avec succès", "success")
        return redirect(url_for('dashboard_patients'))

    # --- RESET PASSWORD ---
    @app.route('/reset-password', methods=['GET', 'POST'])
    def reset_password():
        if request.method=='POST':
            rpps = request.form['rpps']
            reponse = request.form['reponse_secrete']
            new_password = request.form['new_password']
            user = Admin.query.filter_by(rpps=rpps).first()
            if not user:
                flash("❌ RPPS introuvable", "danger")
                return redirect(url_for('reset_password'))
            if check_reponse_secrete_hash(user, reponse):
                user.password_hash = set_password(new_password)
                db.session.commit()
                flash("✅ Mot de passe réinitialisé avec succès", "success")
                return redirect(url_for('login'))
            else:
                flash("❌ Réponse secrète incorrecte", "danger")
                return redirect(url_for('reset_password'))
        return render_template('reset_password.html')
