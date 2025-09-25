import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
migrate = Migrate()

def create_app():
    # 🔹 Chemin vers le dossier templates
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    app = Flask(__name__, template_folder=template_dir)

    # 🔹 Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:@localhost/medicard"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🔹 Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 🔹 Import et initialisation des routes
    from medcard.routes import init_routes
    init_routes(app)

    # 🔹 Crée les tables si elles n'existent pas
    with app.app_context():
        db.create_all()

    return app

