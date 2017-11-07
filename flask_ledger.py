from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
