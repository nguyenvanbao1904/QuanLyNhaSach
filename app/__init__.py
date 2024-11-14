from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345678@localhost/quanlynhasach?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "kjasdlkasjdlkasdjlkasdjalskdjalskdj"

db = SQLAlchemy(app)
