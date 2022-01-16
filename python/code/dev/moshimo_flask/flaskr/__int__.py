from flask import Flask
from flaskr.database import db
from .views.user import tickers
import config

def create_app():

  app = Flask(__name__)

  # DB設定を読み込む
  app.config.from_object('config.Config')
  db.init_app(app)

  app.register_blueprint(tickers, url_prefix='/tickers')

  return app

app = create_app()