from wtforms import (Form, BooleanField, StringField, PasswordField, 
    validators,SelectField,ValidationError)

class Tickers_Form(Form):
    #form & validate
    ticker = StringField('ticker (ex:SOXL)', [validators.DataRequired(), 
        validators.Regexp('^[0-9a-z]+$', message='半角英数のみ入力可能')])
    stock_name = StringField('stock_name (ex:SOXL / Direxion デイリー 半導体株 ブル 3倍 ETF)', 
        [validators.DataRequired()])
    purchase_format = SelectField('purchase_format (ex:ETF)', 
        choices=[(''),('ETF')], validate_choice = True)
    currency = SelectField('currency (ex:USD,JPY)通貨',
        choices=[(''),('USD'), ('JPY')], validate_choice = True)
    exchange = SelectField('exchange (ex:NYSE Arca) 上場取引所', 
        choices=[(''),('NYSE Arca')], validate_choice = True)
    
    #selectfieldのみ入力必須の関数不可なので↓でvalidate
    def validate_purchase_format(form, purchase_format): 
        if purchase_format.data == "": 
            raise ValidationError("このフィールドは入力必須です") 
    def validate_currency(form, currency): 
        if currency.data == "": 
            raise ValidationError("このフィールドは入力必須です") 
    def validate_exchange(form, exchange): 
        if exchange.data == "": 
            raise ValidationError("このフィールドは入力必須です") 


"""
    これは記入例。wtforms公式を見るとよい
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
"""