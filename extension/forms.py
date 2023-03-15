from wtforms import Form, PasswordField, validators, StringField, SelectField, DateField, IntegerField, HiddenField
from wtforms.validators import ValidationError
import re
from extension.functions import digits

char = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
num = "0123456789"
spec_char="!@#$%^&*()_+[]\\;'./,<>?:{}|+_\""

def validate_userid(form,field):
    num_flag = False
    alph_flag = False

    if len(field.data) < 6:
        raise ValidationError("Must be at least 6 characters long")
    ### add one that needs numbers
    for n in num:
        if n in field.data:
            num_flag = True
            break
    for a in char:
        if a in field.data:
            alph_flag = True
    if num_flag == False:
        raise ValidationError("Must have at least 1 number")
    if alph_flag == False:
        raise ValidationError("Must have have alphabets")

    for i in field.data:
        if i in spec_char:
            raise ValidationError("No special characters allowed")

def validate_fname(form, field):
    for i in field.data:
        if i not in char:
            raise ValidationError("Only alphabets are allowed")

def validate_lname(form, field):
    for i in field.data:
        if i not in char:
            raise ValidationError("Only alphabets are allowed")

def validate_phone(form, field):
    for i in field.data:
        if i not in num:
            raise ValidationError("Only numbers are allowed")

def check_email(Form, field):
    pattern = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not (re.search(pattern,field.data)):
        raise ValidationError("Please enter an email")

# def validate_password(form, field):
#     pattern = "^(?=.[A-Za-z])(?=.\d)(?=.[@$!%#?&])[A-Za-z\d@$!%*#?&]{8,}$"
#     if not (re.search(pattern, field.data)):
#         print('reaches')
#         raise ValidationError("You need a stronger password")


class LoginForm(Form):
    userid = StringField("",[validators.DataRequired()],render_kw={"placeholder":"User ID"})
    password = PasswordField("",[validators.DataRequired()], render_kw={"placeholder":"Password"})

class Register(Form):
    firstname = StringField("",[validators.DataRequired(), validate_fname],render_kw={"placeholder":"First Name"})
    lastname = StringField("",[validators.DataRequired(), validate_lname],render_kw={"placeholder":"Last Name"})
    userid = StringField("",[validators.DataRequired(),validate_userid],render_kw={"placeholder":"User ID"})
    email = StringField("",[validators.DataRequired(),check_email], render_kw={"placeholder":"Email"})
    phone = StringField("" , [validators.DataRequired(),validate_phone,validators.Length(min=8)], render_kw={"placeholder":"Phone"})
    password = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Password"})

class ForgotPass(Form):
    username = StringField("",[validators.DataRequired()],render_kw={"placeholder":"User ID"})

class ResetPass(Form):
    password = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Password"})
    confirm_pass = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Confirm Password"})

class AccountForm(Form):
    username = StringField("",[validators.DataRequired()],render_kw={"placeholder":"User ID"})
    password = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Password"})
    confirm_pass = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Confirm Password"})




class TrackNoConv(Form):
    convention = SelectField('',[validators.DataRequired()], choices=[('alnum', 'Alphanumeric'), ('num', 'Numbers ONLY')])
class TrackNoConv2(Form):
    convention2 = SelectField('',[validators.DataRequired()], choices=[('alnum', 'Alphanumeric'), ('num', 'Numbers ONLY')])

class TrackNoLen(Form):
    len_trackno = StringField('', [validators.DataRequired(), validate_phone])
class TrackNoLen2(Form):
    len_trackno2 = StringField('', [validators.DataRequired(), validate_phone])

class TrackNoAlpha(Form):
    leading_alpha = StringField('', [validators.DataRequired(), validate_fname])
class TrackNoAlpha2(Form):
    leading_alpha2 = StringField('', [validators.DataRequired(), validate_fname])

class TrackNoStart(Form):
    starting_no = StringField('',[validators.DataRequired(),validators.Length(max=digits) , validate_phone])
class TrackNoStart2(Form):
    starting_no2 = StringField('',[validators.DataRequired(),validators.Length(max=digits) , validate_phone])

class EmailNotif(Form):
    email = StringField("",[validators.DataRequired(),check_email])

class EmailToken(Form):
    token = StringField("",[validators.DataRequired()])

class TwilioSID(Form):
    account_sid = StringField("",[validators.DataRequired()])

class TwilioToken(Form):
    auth_token = StringField("",[validators.DataRequired()])


class ExpCounterStart(Form):
    start = DateField("",[validators.DataRequired()],format='%Y-%m-%d')

class ExpCounterPeriod(Form):
    years = IntegerField("Years: ",[validators.InputRequired(), validators.NumberRange(min=0,max=6)])
    months = IntegerField("Months: ",[validators.InputRequired(), validators.NumberRange(min=0,max=12)])
    days = IntegerField("Days: ",[validators.InputRequired(), validators.NumberRange(min=0,max=365)])

class ExpKey(Form):
    key = PasswordField("",[validators.DataRequired()],render_kw={"placeholder":"Key"})



class CredentialsUser(Form):
    userid = StringField("",[validators.DataRequired()],render_kw={"placeholder":"User ID"})

class CredentialsPassword(Form):
    password = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Change Password"})
    confirm_pass = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Confirm Password"})

class ChangeExpKey(Form):
    password = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Expiry Key"})
    confirm_pass = PasswordField("",[validators.DataRequired(), validators.Length(min=8)], render_kw={"placeholder":"Confirm Expiry Key"})