import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['API_URL'] = os.getenv('API_URL')
    app.config['API_KEY'] = os.getenv('API_KEY')
    app.config['DATABASE'] = os.getenv('DATABASE')
    
    from app.main import bp as main_bp
    from app.Overzichtspagina import bp as projects_bp
    from app.blockly import bp as blockly_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(blockly_bp, url_prefix='/blockly')
    return app