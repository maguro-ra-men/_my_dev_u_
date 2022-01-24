import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import sys
sys.path.append("C:\\Users\\kazu\\_my_dev_u_\\python\\code\\dev\\moshimo_flask\\flaskr")

from flask import Flask, request, redirect
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, ValidationError

from db import *
from models.ztest_class import Tickers
from models.ztest_forms import RegistrationForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "sample1201"

@app.route("/")
def index():
    return render_template ('index.html')

@app.route("/test_html",methods=['GET','POST'])
def test_create():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        stock_name = request.form.get('stock_name')
        ticker = request.form.get('ticker')
        purchase_format = request.form.get('purchase_format')
        currency = request.form.get('currency')
        exchange = request.form.get('exchange')
        post = Tickers(stock_name=stock_name,ticker=ticker,
                        purchase_format=purchase_format,currency=currency,
                        exchange=exchange)

        session.add(post)
        session.commit()
        return redirect('/test_html')
    else:
        return render_template ('test_html.html', form=form)