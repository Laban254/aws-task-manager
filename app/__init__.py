from flask import Flask
from .auth import auth_blueprint, main_blueprint
from .media import media_blueprint
from .db import db, test_db_connection, test_s3_connection
from .config import Config
from flask_migrate import Migrate
from flask.cli import with_appcontext
from sqlalchemy import text
from .services.listen_for_thumbnail_update import start_sqs_listener

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    db.init_app(app)
    test_db_connection(app)
    # test_s3_connection(app)

    start_sqs_listener(app)

    migrate = Migrate(app, db)
    @app.cli.command("db-drop-all")
    @with_appcontext
    def db_drop_all():
        """Drops all tables from the database and removes the alembic_version table"""
        
        # Drop the alembic_version table (if it exists)
        try:
            db.session.execute(text("DROP TABLE IF EXISTS alembic_version;"))
            db.session.commit()
            print("alembic_version table has been dropped.")
        except Exception as e:
            print(f"Error dropping alembic_version table: {e}")
        
        # Drop all other tables
        db.drop_all()
        print("All tables have been dropped!")

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(media_blueprint, url_prefix='/media')

    return app
