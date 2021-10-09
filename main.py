from src.modules import *
from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return "<p>Hello</p>"




