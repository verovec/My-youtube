import connexion
from connexion.resolver import RestyResolver
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
sys.path.insert(1, '/mailer')
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(extra_config_settings={}):
    appli = connexion.FlaskApp(__name__, specification_dir='swagger/')
    appli.app.config.from_object(Config)
    appli.app.config.update(extra_config_settings)
    db.init_app(appli.app)
    migrate.init_app(appli.app, db)
    appli.add_api('service.yaml', resolver=RestyResolver('api'))
    return appli.app
