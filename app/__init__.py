import os

from flask import Flask

# create and configure the app

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'ATS.sqlite'),
)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

from . import database
database.init_app(app)

from . import auth
app.register_blueprint(auth.bp)

from . import query_based
app.register_blueprint(query_based.bp)

from . import profile
app.register_blueprint(profile.bp)

from . import expressions
app.register_blueprint(expressions.bp)

from . import summarizer
app.register_blueprint(summarizer.bp)

from . import launcher
app.register_blueprint(launcher.bp)
app.add_url_rule('/', endpoint='launch')

