from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345678@localhost/quanlynhasach?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "kjasdlkasjdlkasdjlkasdjalskdjalskdj"

db = SQLAlchemy(app)
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

migrate = Migrate(app, db)

from .models import *