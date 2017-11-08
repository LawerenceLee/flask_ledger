from flask import (Flask, g, render_template,
                   flash, redirect, url_for,
                   abort)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = "aasdfasdf;aosihasgo*(&^Uhkewjd7efI&%$iygkjbsd"


@app.route('/')
def index():
    accounts = models.Account.select()
    return render_template('index.html', accounts=accounts)


if __name__ == "__main__":
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)
