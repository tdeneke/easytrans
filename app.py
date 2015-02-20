from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

@app.route('/')
def hello():
    #print os.environ['APP_SETTINGS']
    #print os.environ['DATABASE_URL']
    return "easytrans helloworld!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if  __name__ == '__main__':
    app.run()
