from flask_wtf import FlaskForm
from wtforms import validators, StringField, IntegerField, validators, TextAreaField, ValidationError
from custom_forms import *

class UserForm(FlaskForm):
    message_required = "必須項目です"
    name = StringField("名前")
    age = IntegerField('年齢', widget=NumberInput(),  validators=[validators.InputRequired(message_required)])
    description = TextAreaField("自己紹介")
    topics = StringField("気になるトピック (カンマ区切りで入力してください。)")

    def validate_name(self, name):
        if name.data == "":
            raise ValidationError("名前を入力してください")

    def validate_age(self, age):
        if age.data == "":
            raise ValidationError("年齢を入力してください")

    def validate_description(self, description):
        if description.data == "":
            raise ValidationError("本文を入力してください。")

        if len(description.data) < 10:
            raise ValidationError("本文は10文字以上にしてください。")

    def validate_topics(self, topics):
        topic_list = topics.data.strip().split(",")
        if len(topic_list) < 3:
            raise ValidationError("好きなトピックを少なくとも３つ教えてください。")