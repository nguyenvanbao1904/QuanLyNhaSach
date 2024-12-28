from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
from threading import Thread


from app.redis_tasks import pubsub_worker
from dotenv import load_dotenv
import cloudinary
import os
import pymysql
from sqlalchemy import create_engine
app = Flask(__name__)
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}?charset=utf8mb4"
)

# Cấu hình SSL cho kết nối MySQL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'ssl': {
            'ca': "./app/static/pem/ca.pem",
        }
    }
}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "kjasdlkasjdlkasdjlkasdjalskdjalskdj"
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

migrate = Migrate(app, db)

#cloudinary
cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET'))


redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# Cấu hình notify-keyspace-events
try:
    redis_client.config_set('notify-keyspace-events', 'Ex')
    print("Cấu hình notify-keyspace-events thành công!")
    current_config = redis_client.config_get('notify-keyspace-events')
    print(f"notify-keyspace-events: {current_config}")
except redis.exceptions.RedisError as e:
    print(f"Lỗi khi cấu hình notify-keyspace-events: {e}")

worker_thread = Thread(target=pubsub_worker.handle_order_expiration, daemon=True)
worker_thread.start()

def create_admin_user():
    from app import dao
    from app.models import User, AccountRole
    admin_user = dao.get_user_by_username('admin')
    if not admin_user:
        dao.add_user(username='admin', password='12345678aA', first_name='admin', last_name='1', accountrole=AccountRole.ADMIN, avatar=None, phone_number="0886201641", email="bao19042004@gmai.com")
        print("Admin user created successfully.")

@app.before_request
def create_admin_on_start():
    create_admin_user()



