from flask import Flask
from database import db_session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

