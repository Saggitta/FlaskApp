import os

from flask import Flask, session

from config import config
from auth.views import auth_bp

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = config["WEBAPP"]["SECRET_KEY"]
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "flaskr.sqlite")
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route("/hello")
    def hello():
        return session.get('user')

    from . import db

    db.init_app(app)

    # from . import auth

    # app.register_blueprint(auth.bp)

    from . import notes

    app.register_blueprint(notes.bp)
    app.register_blueprint(auth_bp, url_prefix='/')
    app.add_url_rule("/", endpoint="index")

    return app
