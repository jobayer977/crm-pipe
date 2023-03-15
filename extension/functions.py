from flask import flash, redirect, url_for, session
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from datetime import date
from fpdf import FPDF

from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger, PdfFileReader
import io, os

from twilio.rest import Client
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import binascii
import random
import dropbox

import mysql.connector
from mysql.connector import Error

import shelve

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'


connection = mysql.connector.connect(host="mymysqlcontainer",
                                     #database='database',
                                     database="order_db",
                                     user="root",
                                    #password='4ntelopeXD!')  ######### change accordingly
                                     password="Adev123..",
                                     port=3306
                                    )  ######### change accordingly




# Create a function to hash the password
def hash_password(password):

    return generate_password_hash(password)


# Create a function to check if the password matches
def verify_password(password, hashed_password):
    # Get the salt and key from the hashed password


    # Check if the hashed passwords match
    return check_password_hash(hashed_password, password)
cursor = connection.cursor()

with open('config.txt', 'r') as config:
    clines = config.readlines()
    config.close()

for i in clines:
    clines = i.strip().split(',')

convention_choice = clines[0]

digits = int(clines[1])  ## digits
start_num = int(clines[2])
choice_of_alph = clines[3]  ## choice_of_alph
num_of_alph = len(choice_of_alph)  ## num_of_alph

convention_choice2 = clines[4]

digits2 = int(clines[5])  ## digits
start_num2 = int(clines[6])
choice_of_alph2 = clines[7]  ## choice_of_alph
num_of_alph2 = len(choice_of_alph)  ## num_of_alph

account_sid = clines[10]  ##account_sid
auth_token = clines[11]  ##auth_token

SENDER = clines[8]  ## SENDER
GMAIL_PASS = clines[9]  ## GMAIL_PASS

with open('exp_pass.txt', 'r') as exp_pass:
    a = exp_pass.readlines()
    exp_pass.close()

exp_salt = a[0][0:-1].encode('utf-8')
exp_hash = a[1].encode('utf-8')


def check_expiration():
    with open('config.txt', 'r') as config:
        clines = config.readlines()
        config.close()

    for i in clines:
        clines = i.strip().split(',')

    expiration_start = clines[12]
    expiration_period = clines[13]
    expiration_status = "running"

    if expiration_start and expiration_period != "":

        period_list = expiration_period.split("-")
        expiration_diff = datetime.timedelta(days=int(period_list[0])*365 + int(period_list[1])*30 + int(period_list[2]))
        expiration_start = datetime.date(int(expiration_start[0:4]),int(expiration_start[5:7]),int(expiration_start[8:]))


        if expiration_start + expiration_diff <= datetime.date.today():
            expiration_status = "expired"
    return expiration_status

def generate_alnum_track_no():
    # digits = 3  ### change digits according to preference, make sure to drop table if changed
    # num_of_alph = 2  ### change number according to preference, make sure to drop table if changed
    # choice_of_alph = 'DO'  ###choose the letters you would prefer the tracking number to start with, length must be equals to num_alph

    # start_num = 1  ## can be absolutely anything

    connection.commit()
    sql_select = """SELECT MAX(Track_no) FROM `Order`;"""

    cursor = connection.cursor()
    cursor.execute(sql_select)
    records = cursor.fetchall()

    if records[0][0] == None:
        lead_num = digits - len(str(start_num))
        track_no = choice_of_alph + lead_num * '0' + str(start_num)  ## for now only 1 starting alphabet
        return track_no
    else:
        records = int(records[0][0][num_of_alph:])
        records = int(records) + 1

        for i in range(1, digits):
            if len(str(records)) == i:
                lead_num = digits - i
                track_no = choice_of_alph + lead_num * '0' + str(records)
                return track_no


def generate_num_track_no():
    # digits = 4  ### change digits according to preference, make sure to drop table if changed

    # start_num = 1  ## can be absolutely anything

    connection.commit()
    sql_select = """SELECT MAX(Track_no) FROM `Order`;"""

    cursor = connection.cursor()
    cursor.execute(sql_select)
    records = cursor.fetchall()
    print(start_num)
    if records[0][0] == None:
        lead_num = digits - len(str(start_num))
        track_no = '0' * lead_num + str(start_num)
        return track_no
    else:
        records = records[0][0]
        records = int(records) + 1

        for i in range(1, digits):
            if len(str(records)) == i:
                lead_num = digits - i
                track_no = '0' * lead_num + str(records)
                return track_no

def generate_alnum_track_no2():
    # digits = 3  ### change digits according to preference, make sure to drop table if changed
    # num_of_alph = 2  ### change number according to preference, make sure to drop table if changed
    # choice_of_alph = 'DO'  ###choose the letters you would prefer the tracking number to start with, length must be equals to num_alph

    # start_num = 1  ## can be absolutely anything

    connection.commit()
    sql_select = """SELECT MAX(Track_no) FROM Maintenance;"""

    cursor = connection.cursor()
    cursor.execute(sql_select)
    records = cursor.fetchall()

    if records[0][0] == None:
        lead_num = digits2 - len(str(start_num))
        track_no = choice_of_alph2 + lead_num * '0' + str(start_num2)  ## for now only 1 starting alphabet
        return track_no
    else:
        records = int(records[0][0][num_of_alph2:])
        records = int(records) + 1

        for i in range(1, digits2):
            if len(str(records)) == i:
                lead_num = digits2 - i
                track_no = choice_of_alph2 + lead_num * '0' + str(records)
                return track_no


def generate_num_track_no2():
    # digits = 4  ### change digits according to preference, make sure to drop table if changed

    # start_num = 1  ## can be absolutely anything

    connection.commit()
    sql_select = """SELECT MAX(Track_no) FROM Maintenance;"""

    cursor = connection.cursor()
    cursor.execute(sql_select)
    records = cursor.fetchall()
    print(start_num)
    if records[0][0] == None:
        lead_num = digits2 - len(str(start_num2))
        track_no = '0' * lead_num + str(start_num2)
        return track_no
    else:
        records = records[0][0]
        records = int(records) + 1

        for i in range(1, digits2):
            if len(str(records)) == i:
                lead_num = digits2 - i
                track_no = '0' * lead_num + str(records)
                return track_no



class User(UserMixin):
    def __init__(self, id, userid, fname, lname, phone, password, role):
        self.id = id
        self.userid = userid
        self.fname = fname
        self.lname = lname
        self.phone = phone
        self.password = password
        self.role = role

    def repr(self):
        return 'userid:' + self.userid + ' | full name:' + self.fname + ' ' + self.lname + ' | phone:' + str(
            self.phone) + ' | phone:' + self.phone + ' | password:' + str(self.password) + ' | role:' + str(self.role)

    def get_id(self):
        return str(self.id)

    def get_userid(self):
        return self.userid

    def get_fname(self):
        return self.fname

    def get_lname(self):
        return self.lname

    def get_user_phone(self):
        return self.phone

    def get_user_password(self):
        return self.password

    def get_role(self):
        return self.role

    def set_role(self, role):
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class TransferData:
    def __init__(self,access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)


access_token = 'sl.BG-kUfmBcqK9VJfIDZS3G-jYvBHYKNCCKHRZGMdf-8lvhEqObZVtcJh-p77V_09yEtyI4Xd6XY0gLZKrgBX_Moer2EVGSq-uL7mlTHDoSpVRVpmfqVbVd1xy4FJ89P-NyRrhbl0'
transferData = TransferData(access_token)


def create_account(userid, fname, lname, phone, password, email):
    salt = ""
    hashed_password = hash_password(password)
    print(hashed_password)

    role = "User"

    sql_insert = """INSERT INTO User (UserID, FName, LName, Phone, Password, Salt, Email, Role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    args = (userid, fname, lname, phone, hashed_password, salt, email, role)
    try:
        cursor.execute(sql_insert, args)
        # client.contacts.create(lists="0", phone="+65"+str(phone))
        connection.commit()
        flash('Account has been created')
    except:
        flash('UserID, Phone Number or Email is already in use')


with open('server_adm.txt', 'r') as file:
    lines = file.readlines()
    file.close()

adm_salt = lines[0][0:-1]
adm_salt = adm_salt.encode('utf-8')

org_hash = lines[1][0:-1]
org_hash = org_hash.encode('utf-8')


def validate_user(userid, input_password):
    connection.commit()
    sql_select = """ SELECT * FROM User WHERE UserID = '{}' """

    cursor = connection.cursor()
    cursor.execute(sql_select.format(userid))
    records = cursor.fetchone()

    # if records == None:
    #     adm_credentials = userid + input_password
    #     if check_password_hash(adm_credentials, org_hash, adm_salt) == True:
    #         user = User(0, userid, userid, "server", "admin", "password", "SvrAdm")
    #         session['current'] = {'userid': userid, 'role': 'SvrAdm'}
    #         login_user(user)
    #         return True
    #     else:
    #         flash('Invalid UserID or Password')
    #
    # else:

    if records == None:
        flash('Invalid UserID or Password')

    else:
        id_no = records[0]
        db_userid = records[1]
        fname = records[2]
        lname = records[3]
        phone = records[4]
        salt = records[6].encode('utf-8')
        role = records[8]

        db_hashed_password = records[5]

        if userid == db_userid:
            if role == 'SvrAdm':
                input_password = input_password
            else:
                if check_expiration() == "expired":
                    flash('The Application has expired, please contact your Management.')
                    return False

            print(input_password)
            print(db_hashed_password)
            print(verify_password(input_password, db_hashed_password))
            if verify_password(input_password, db_hashed_password):
                user = User(id_no, db_userid, fname, lname, phone, db_hashed_password, role)
                session['current'] = {'userid': db_userid, 'role': role}
                login_user(user)
                return True
            else:
                flash('Invalid UserID or Password')


def get_current_date():
    today = date.today()

    day = today.strftime("%Y-%m-%d")
    return day


def create_pdf(caller_desc_args, type_of_fault_args, fault_details_args, action_taken_args, desc_args):

    track_no = caller_desc_args[0]
    lift_no = caller_desc_args[1]

    sql_select = """SELECT Company_name,Site_addr FROM `Order` WHERE Track_no = '{}'"""
    sql_args = track_no
    #
    #
    cursor = connection.cursor()
    connection.commit()
    cursor.execute(sql_select.format(sql_args))
    records = cursor.fetchall()
    records = records[0]

    company_name = records[0]
    site_addr = records[1]

    # create FPDF object
    # Layout ('P', 'L')
    # Unit ('mm', 'cm', 'in')
    # format ('A3', 'A4' (default), 'Letter', 'Legal', (100, 150))
    pdf = FPDF('P', 'mm')

    # Set auto page break
    pdf.set_auto_page_break(auto=True, margin=15)

    # Adding a page
    pdf.add_page()

    # specify fonts (times, courier, helvetica, symbol, zpfdingbars)
    # 'B' (Bold), 'U' (Underline), 'I' (Italics), '' (Regular), combo (e.g. ('BU'))
    pdf.set_font('helvetica', 'B', 16)
    # pdf.set_text_color(255,50,50)

    # Add text
    # w = width, h = height,
    # ln = (0 False, 1 True - move down a line)
    # border = (0 False, 1 True - draw a border)
    # align = ('L' Left, 'C' Center, 'R' Right)

    # COMPANY LOGO AND NAME
    pdf.image('excelift.jpeg', 10, 10, 50)
    pdf.cell(190, 4, "EXCELIFT PTE LTD", ln=1, border=0, align='R')

    # COMPANY ADDRESS AND CONTACT
    pdf.set_font('helvetica', '', 8)
    pdf.cell(190, 4, "61 Kaki Bukit Avenue 1 #04-16", ln=1, border=0, align='R')
    pdf.cell(0, 4, "Shun Li Industrial Park Singapore 417943", ln=1, border=0, align='R')
    pdf.cell(190, 4, "Tel: (65) 6848 4260 Fax: (65) 6848 4261", ln=1, border=0, align='R')
    pdf.cell(0, 4, "Reg. No.: 199904532N", ln=1, border=0, align='R')
    pdf.cell(0, 4, "24-Hours Service Tel: 6356 8738", ln=1, border=0, align='R')
    pdf.line(5, 35, 205, 35)
    pdf.cell(0, 2, "", ln=1, border=0, align='R')

    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(105, 10, "Service Report", ln=0, border=0, align='R')
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 10, "S/No: " + track_no, ln=1, border=0,
             align='C')  # Replace 14159 with actual generated tracking number

    # pdf.set_font('helvetica', 'U', 9)
    # pdf.cell(-50, 7, company_name, ln=0, border=0, align='L')
    pdf.set_font('helvetica', '', 9)
    pdf.cell(105, 7, "Company Name: " + company_name, ln=1, border=0,
             align='L')  # Inset Company name on top of the line

    # pdf.set_font('helvetica', 'U', 9)
    # pdf.cell(-50, 7, site_addr, ln=0, border=0, align='L')
    pdf.set_font('helvetica', '', 9)
    pdf.cell(105, 7, "Site Address:    " + site_addr, ln=0, border=0,
             align='L')  # Inset Site Address on top of the line

    if lift_no != '':
        pdf.set_font('helvetica', 'U', 9)
        lead_space = 13 - len(lift_no)
        pdf.cell(0, 7, lead_space * "\t" + lift_no, ln=0, border=0, align='R')
        pdf.set_font('helvetica', '', 9)
        pdf.cell(-13, 7, "Lift No: ", ln=1, border=0, align='R')  # Inset Lift No. on top of the line
        # pdf.cell(0, 7 , "\t\t\t\t\t\t\t\t\t\t\t"+lift_no, ln=0, border=0, align='R')
    else:
        pdf.set_font('helvetica', '', 9)
        pdf.cell(-12, 7, "Lift No: _______", ln=1, border=0, align='R')  # Inset Lift No. on top of the line
    pdf.line(10, 61, 200, 61)

    sections = ["Caller's Description", "Type of Fault", "Fault Details", "Action Taken"]
    caller_desc_title = [" Breakdown", " Travel Noise", " Man Trap", " Not Levelling", " Light / Fan",
                         " Button / Indicator", "Others: "]
    type_of_fault_title = [" FALSE Call", " Power Failure", " Misuse", " Water Ingrees", " Equipment Failure",
                           " Vandalism", "Others: "]
    fault_details_title = [" Hydraulic Drive", " ARD/EBOPS", " Hydraulic System", " Controller", " Hoist Machine",
                           " Car Station / Circuit", "Landing Door /Car Door", " Car Cage / Counterweight",
                           " Landing Station Circuit", " GOVERNOR / Safety Gear", " Light / Fan Fitting",
                           " Off-Seal Leaking", " Cartop / Shaft Electrical", " Security System",
                           " Cartop / Shaft Mechanical", " Supervisory / Lobby Vision", " Others: "]
    action_taken_title = [" Repaired / Serviced", " Shutdown", " Replaced Parts", " To Monitor / Follow Up",
                          " Quotation Required", "Others: "]

    name_list = []

    for header in sections:
        if header == "Caller's Description":
            name_list = caller_desc_title
            args = caller_desc_args
        if header == "Type of Fault":
            name_list = type_of_fault_title
            args = type_of_fault_args
        if header == "Fault Details":
            name_list = fault_details_title
            args = fault_details_args
        if header == "Action Taken":
            name_list = action_taken_title
            args = action_taken_args

        skip_count = 0
        if len(name_list) % 2 == 0:
            # skip = len(name_list)//2
            skip = (len(name_list) - 1) // 3
        else:
            skip = (len(name_list) - 1) / 3
            if int(str(skip)[2]) > 0:
                skip = int(str(skip)[0]) + 1
            else:
                skip = int(str(skip)[0])
        # Replace "Y" with a check mark, and leave blank for "N"
        pdf.set_font('helvetica', 'BU', 12)
        pdf.cell(105, 10, header, ln=1, border=0, align='L')

        idx = 2
        for i in range(len(args) - 1):
            line = 0

            if i > 1:
                label = name_list[i - 2]

                if args[i] == 'Y':
                    pdf.set_font('helvetica', 'U', 9)
                    pdf.cell(10, 6, "\t\t\t\tX\t\t\t", ln=0, border=0, align='L')
                else:
                    if i > 1:
                        pdf.set_font('helvetica', '', 9)
                        pdf.cell(10, 6, "_____", ln=line, border=0, align='L')
                pdf.set_font('helvetica', '', 9)

                if (skip_count < skip and i - 2 == idx) or label == name_list[-2]:
                    line = 1
                    skip_count += 1
                    idx += 3
                else:
                    line = 0
                # if name_list.index(label) % 2 > 0 and skip_count < skip:
                #     line = 1
                #     skip_count += 1
                # else:
                #     line = 0
                pdf.cell(60, 6, label, ln=line, border=0, align='L')

        pdf.cell(15, 6, "Others: ", ln=0, border=0, align='L')
        print(args)
        if args[-1] != 'N':
            pdf.cell(0, 6, args[-1], ln=1, border=1, align='J')
        else:
            pdf.cell(0, 6, "", ln=1, border=1, align='J')

        if header == "Caller's Description":
            pdf.line(10, 89, 200, 89)
        if header == "Type of Fault":
            pdf.line(10, 117, 200, 117)
        if header == "Fault Details":
            pdf.line(5, 169, 205, 169)
        if header == "Action Taken":
            pdf.line(5, 197, 205, 197)

    # Needs to add "Completed", "Outstanding" and "Others", Replace "Y" with a check mark, and leave blank for "N"
    pdf.set_font('helvetica', 'BU', 12)
    pdf.cell(105, 10, "Description of Work Done", ln=1, border=0, align='L')
    pdf.set_font('helvetica', '', 9)
    if desc_args[2] == 'Y':
        pdf.set_font('helvetica', 'U', 9)
        pdf.cell(10, 7, "\t\t\t\tX\t\t\t", ln=0, border=0, align='L')
        pdf.set_font('helvetica', '', 9)
        pdf.cell(60, 7, " Completed", ln=0, border=0, align='L')
    else:
        pdf.set_font('helvetica', '', 9)
        pdf.cell(70, 7, "_____" + " Completed", ln=0, border=0, align='L')

    if desc_args[3] == 'Y':
        pdf.set_font('helvetica', 'U', 9)
        pdf.cell(10, 7, "\t\t\t\tX\t\t\t", ln=0, border=0, align='L')
        pdf.set_font('helvetica', '', 9)
        pdf.cell(60, 7, " Outstanding", ln=0, border=0, align='L')
    else:
        pdf.set_font('helvetica', '', 9)
        pdf.cell(70, 7, "_____" + " Outstanding", ln=0, border=0, align='L')

    if desc_args[4] == 'Y':
        pdf.set_font('helvetica', 'U', 9)
        pdf.cell(10, 7, "\t\t\t\tX\t\t\t", ln=0, border=0, align='L')
        pdf.set_font('helvetica', '', 9)
        pdf.cell(20, 7, " Others", ln=1, border=0, align='L')
    else:
        pdf.set_font('helvetica', '', 9)
        pdf.cell(30, 7, "____ Others", ln=1, border=0, align='L')
    pdf.cell(190, 7, desc_args[1], ln=1, border=1, align='L')
    pdf.line(5, 221, 205, 221)

    # pdf.set_font('helvetica', 'BU', 12)
    pdf.cell(105, 10, "Client's Feedback (If any)", ln=1, border=0, align='L')
    pdf.set_font('helvetica', '', 9)
    pdf.cell(190, 7, "", ln=1, border=1, align='c')
    pdf.cell(190, 2, "", ln=1, border=0, align='C')
    pdf.cell(100, 18, "", ln=0, border=1, align='L')  # Place Assignee's Signature in cell
    pdf.cell(0, 18, "", ln=1, border=1, align='R')  # Place Client's Signature in cell
    pdf.cell(70, 7, "Serviceman Name / Sign", ln=0, border=0, align='L')  # Insert Assignee's name
    pdf.cell(0, 7, "Client Name / Sign", ln=1, border=0, align='R')
    pdf.cell(0, 3, "", ln=1, border=0, align='J')
    pdf.cell(50, 6, "On Site Date: ", ln=0, border=0, align='L')  # Create date picker in checklist, insert date here
    pdf.cell(112, 6, "Handover Date: ", ln=0, border=0, align='L')
    pdf.cell(0, 6, "Date: ", ln=1, border=0, align='L ')  # Create date picker in checklist, insert date here
    pdf.cell(50, 6, "Take Over Time: ", ln=0, border=0, align='L')  # Create time picker in checklist, insert time here
    pdf.cell(0, 6, "Time Out: ", ln=0, border=0, align='L')  # Create time picker in checklist, insert time here

    pdf.output('documents/' + track_no + '.pdf')  # Output to Documents in Dropbox
    pdf.close()

def upload_file(track_no, file_from, index):
        try:
            file_to = '/signed_docs/' + track_no + 'sign.pdf'  # The full path to upload the file to, including the file name
            transferData.upload_file(file_from, file_to)
            return True
        except:
            try:
                file_to = '/signed_docs/' + track_no + "-" + str(index) + 'sign.pdf'  # The full path to upload the file to, including the file name
                index += 1
                transferData.upload_file(file_from, file_to)
                return True
            except:
                return False

def add_sig(track_no, review, onsite, takeover, handover, timeout):
    in_pdf_file = "documents/" + track_no + ".pdf"
    out_pdf_file = "documents/" + track_no + "sign.pdf"

    assgnee = "temp/" + track_no + "assgnee.png"
    client = "temp/" + track_no + "client.png"

    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.setFontSize(9)
    can.drawString(30, 180, review)

    can.drawImage(assgnee, 100, 65, width=120, preserveAspectRatio=True, mask='auto')
    can.drawImage(client, 400, 65, width=120, preserveAspectRatio=True, mask='auto')
    can.drawString(93, 73, onsite)
    can.drawString(242, 73, handover)
    can.drawString(520, 74, get_current_date())
    can.setFontSize(9)
    can.drawString(105, 57, takeover)
    can.drawString(220, 57, timeout)
    can.showPage()

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    new_pdf = PdfFileReader(packet)

    # read the existing PDF
    f = open(in_pdf_file, "rb")
    existing_pdf = PdfFileReader(f)
    output = PdfFileWriter()

    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # page = existing_pdf.getPage(1)
    # page.mergePage(new_pdf.getPage(1))
    # output.addPage(page)

    outputStream = open(out_pdf_file, "wb")
    output.write(outputStream)
    outputStream.close()
    f.close()

    # file_from = 'documents/' + track_no + 'sign.pdf'
    # # API v2
    # flag = False
    # index = 1

    # while flag == False:
    #     if upload_file(track_no, file_from, index):
    #         flag = True
    #     else:
    #         index += 1


def remove_oldpdf(track_no):
    os.remove("temp/" + track_no + 'assgnee.png')
    os.remove("temp/" + track_no + 'client.png')
    os.remove("documents/" + track_no + ".pdf")
    # os.remove("documents\\" + track_no + "sign.pdf")


def create_pdf2(args,records):
    # create FPDF object
    # Layout ('P', 'L')
    # Unit ('mm', 'cm', 'in')
    # format ('A3', 'A4' (default), 'Letter', 'Legal', (100, 150))
    pdf = FPDF('P', 'mm')

    # Set auto page break
    pdf.set_auto_page_break(auto=True, margin=5)

    # Adding a page
    pdf.add_page()

    # specify fonts (times, courier, helvetica, symbol, zpfdingbars)
    # 'B' (Bold), 'U' (Underline), 'I' (Italics), '' (Regular), combo (e.g. ('BU'))
    pdf.set_font('helvetica', 'B', 7)
    # pdf.set_text_color(255,50,50)
    # pdf.set_fill_color(0, 80, 0) # don't work, WHY?

    # Add text
    # w = width, h = height,
    # ln = (0 False, 1 True - move down a line)
    # border = (0 False, 1 True - draw a border)
    # align = ('L' Left, 'C' Center, 'R' Right)

    # COMPANY LOGO AND NAME
    pdf.image('excelift.jpeg', 9, 8, 38)

    # TYPE FO REPORT
    pdf.set_font('helvetica', 'BU', 10)
    pdf.cell(0, 10, "LIFT SERVICING CHECKLIST", ln=1, border=0, align='R')

    pdf.set_font('helvetica', '', 7)
    pdf.cell(15, 5, "LOCATION: ", ln=0, border=0, align='L')
    pdf.cell(65, 5, records[6], ln=0, border=0, align='L') # Inset "Site Address" here
    pdf.cell(25, 5, "", ln=0, border=0, align='L')
    pdf.cell(40, 5, "CONTRACT TYPE: ", ln=0, border=0, align='R')
    if records[9] == 'Others':
        pdf.cell(40, 5, records[9] + " - " + records[10], ln=1, border=0, align='R') # Inset "Contract type" here
    else:
        pdf.cell(20, 5, records[9], ln=1, border=0, align='R') # Inset "Contract type" here

    pdf.cell(15, 5, "LIFT NO.: ", ln=0, border=0, align='L')
    pdf.cell(65, 5, args[1], ln=0, border=0, align='L') # Inset "Lift No" here

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(25, 5, "", ln=0, border=0, align='L')
    pdf.cell(40, 5, "S/NO.: ", ln=0, border=0, align='R')
    pdf.cell(20, 5, args[0], ln=1, border=0, align='R') # Inset "Tracking No" here

    pdf.set_font('helvetica', '', 7)
    pdf.cell(15, 5, "DATE: ", ln=0, border=0, align='L')
    pdf.cell(65, 5, args[2], ln=1, border=0, align='L') # Inset "Assign Date" here

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(142, 5, "", ln=0, border=0, align='C')
    pdf.cell(50, 5, "SERVICE SCHEDULE", ln=1, border=0, align='C')

    # SERVICE SCHEDULE BOX
    pdf.line(152, 35, 202, 35)
    pdf.line(152, 35, 152, 40)
    pdf.line(202, 35, 202, 40)

    #LEFT 1 VERTICAL
    pdf.line(8, 40, 8, 208)
    #LEFT 2 VERTICAL
    pdf.line(32, 40, 32, 208)
    #LEFT 3 VERTICAL
    pdf.line(152, 40, 152, 208)
    #LEFT 4 VERTICAL
    pdf.line(162, 40, 162, 208)
    #LEFT 5 VERTICAL
    pdf.line(172, 40, 172, 208)
    #LEFT 6 VERTICAL
    pdf.line(182, 40, 182, 208)
    #LEFT 7 VERTICAL
    pdf.line(192, 40, 192, 208)
    #RIGHT VERTICAL
    pdf.line(202, 40, 202, 208)

    # HORIZONTAL LINES
    pdf.line(8, 40, 202, 40)
    pdf.line(8, 43, 202, 43)
    pdf.line(8, 46, 202, 46)
    pdf.line(8, 49, 202, 49)
    pdf.line(8, 52, 202, 52)
    pdf.line(8, 55, 202, 55)
    pdf.line(8, 58, 202, 58)
    pdf.line(8, 61, 202, 61)
    pdf.line(8, 64, 202, 64)
    pdf.line(8, 67, 202, 67)
    pdf.line(8, 70, 202, 70)
    pdf.line(8, 73, 202, 73)
    pdf.line(8, 76, 202, 76)
    pdf.line(8, 79, 202, 79)
    pdf.line(8, 82, 202, 82)
    pdf.line(8, 85, 202, 85)
    pdf.line(8, 88, 202, 88)
    pdf.line(8, 91, 202, 91)
    pdf.line(8, 94, 202, 94)
    pdf.line(8, 97, 202, 97)
    pdf.line(8, 100, 202, 100)
    pdf.line(8, 103, 202, 103)
    pdf.line(8, 106, 202, 106)
    pdf.line(8, 109, 202, 109)
    pdf.line(8, 112, 202, 112)
    pdf.line(8, 115, 202, 115)
    pdf.line(8, 118, 202, 118)
    pdf.line(8, 121, 202, 121)
    pdf.line(8, 124, 202, 124)
    pdf.line(8, 127, 202, 127)
    pdf.line(8, 130, 202, 130)
    pdf.line(8, 133, 202, 133)
    pdf.line(8, 136, 202, 136)
    pdf.line(8, 139, 202, 139)
    pdf.line(8, 142, 202, 142)
    pdf.line(8, 145, 202, 145)
    pdf.line(8, 148, 202, 148)
    pdf.line(8, 151, 202, 151)
    pdf.line(8, 154, 202, 154)
    pdf.line(8, 157, 202, 157)
    pdf.line(8, 160, 202, 160)
    pdf.line(8, 163, 202, 163)
    pdf.line(8, 166, 202, 166)
    pdf.line(8, 169, 202, 169)
    pdf.line(8, 172, 202, 172)
    pdf.line(8, 175, 202, 175)
    pdf.line(8, 178, 202, 178)
    pdf.line(8, 181, 202, 181)
    pdf.line(8, 184, 202, 184)
    pdf.line(8, 187, 202, 187)
    pdf.line(8, 190, 202, 190)
    pdf.line(8, 193, 202, 193)
    pdf.line(8, 196, 202, 196)
    pdf.line(8, 199, 202, 199)
    pdf.line(8, 202, 202, 202)
    pdf.line(8, 205, 202, 205)
    pdf.line(8, 208, 202, 208)
    #pdf.line(8, 212, 202, 212)
    #pdf.line(8, 216, 202, 216)
    #pdf.line(8, 217, 202, 217)
    #pdf.line(8, 220, 202, 220)
    #pdf.line(8, 223, 202, 223)
    #pdf.line(8, 226, 202, 226)

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(20, 3, "MOTOR ROOM", ln=0, border=0, align='C')
    pdf.cell(122, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "S", ln=0, border=0, align='C')
    pdf.cell(10, 3, "3M", ln=0, border=0, align='C')
    pdf.cell(10, 3, "6M", ln=0, border=0, align='C')
    pdf.cell(10, 3, "12M", ln=0, border=0, align='C')
    pdf.cell(10, 3, "CHK", ln=1, border=0, align='C')

    pdf.set_font('helvetica', '', 6)
    pdf.cell(20, 3, "01", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CLEANING & CHECKING BRAKE SLEEVES / SHAFT / PLUNGER", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[3] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "02", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CLEANING BRAKE LINING (MINIMUM THISKNESS 3 MILLIMETERS)", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[4] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "03", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "GENERAL BRAKE ADJUSTMENT & OILING", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[5] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "04", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "GOVERNOR MACHINE, OILING & FUNCTIONING / TENSION PULLEY", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[6] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "05", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "DETECTION OF IRREGULAR NOISE FROM STAND / THRUST BEARINGS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[7] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "06", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK WEARING OF SHEAVE GROOVES / WIRE ROPES", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[8] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "07", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK TRACTION MACHINE CARBON BRUSHES / HOLDER SPRING / sup RINGS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[9] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "08", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "TIGHTENING OF RELAY & TERMINAL SCREWS / CHECK FUSE HOLDER", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[10] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "09", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CLEAN RELAY CONTACTS (MAIN RELAYS ONLY)", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[11] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "10", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK GEAR OIL LEVEL AND OIL LEAKAGE", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[12] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "11", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "GENERAL CLEANING OF MOTOR-ROOM", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[13] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "12", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK EMERGENCY POWER SOURCE - BATTERY BATTERY CHARGER / EBOPS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[14] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "13", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK AND GREASE STAND / MOTOR / THRUST BEARINGS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    if args[15] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(20, 3, "HOISTWAY", ln=1, border=0, align='C')

    pdf.set_font('helvetica', '', 6)
    pdf.cell(20, 3, "14", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CLEAN & LUBRICATE DOOR BAR", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[16] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "15", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK / ADJUST CATCH DEWCE & DOOR LOCK RELATED", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[17] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "16", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK / ADJUST ECCENTRIC ROLLER", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[18] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "17", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "GENERAL CLEANING OF CAR TO", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[19] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "18", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK & ADJUST DOOR PANEL", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[20] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "19", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK & ADJUST MOVABLE CAM", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[21] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "20", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK & ADJUST CAR DOOR CHAIN", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[22] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "21", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK & FILL CAR / COUNTERWEIGHT LUBRICATION CAN", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[23] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "22", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK / REPLACE CAR & LANDING DOOR GUIDE SHOES / DOOR SILLS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[24] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "23", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK WIRE ROPE TENSIONS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[25] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "24", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK GOVERNOR TENSION PULLEY", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[26] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "25", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK GOVERNOR TENSION PULLEY", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[27] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "26", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK SAFETY CATCH MECHANISM / TIGHTEN LIFTING ROD SCREWS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[28] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "27", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK CAR & COUNTERWEIGHT GUIDE SHOES / RAILS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    if args[29] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "28", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "TIGHTEN ALL HOISTWAY BOLTS & NUTS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    if args[30] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "29", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "MEASURE COUNTERWEIGHT RUN-BY (IF <300MM TO FILL IN MEASUREMENT)", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[31] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "30", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK TRAVELLING CABLE / CABLE HANGER", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[32] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "31", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK OIL BUFFER / SPRING BUFFER / BUFFER SWITCH", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[33] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "32", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK INDUCTOR PLATE HUN-BY", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[34] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "33", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK / ADJUST LANDING DOOR WEIGHTS & ROPES", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[35] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "34", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK OPERATION OF OVERLOAD DEVICE, IF APPLICABLE.", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[36] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "35", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK OPERATION OF OVERLOAD COMPENSATING DEVICE. IF ANY.", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[37] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 4, "36", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "OIL COMPENSATION PULLEY AND COMPENSATING ROPE IF APPLICABLE", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[38] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(20, 3, "LIFT CAR", ln=1, border=0, align='C')

    pdf.set_font('helvetica', '', 6)
    pdf.cell(20, 3, "37", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK / REPLACE INDICATOR BULBS IN CAR", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[39] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "38", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK FUNCTION OF ALARM BELLS AND CRIME SYSTEM & LIFT CAR INTERCOM", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[40] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "39", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK IN-CAR PUSH BUTTONS. BULBS & PUSH BUTTONS / REPLACE", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[41] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "40", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK CAR LIGHTING / FAN", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[42] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "41", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK EMERGENCY LIGHT / FAN", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[43] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "42", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CLEANING OF LIGHT AND FAN DIFFUSER", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    if args[44] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(20, 3, "LANDING", ln=1, border=0, align='C')

    pdf.set_font('helvetica', '', 6)
    pdf.cell(20, 3, "43", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK LANDING INDICATOR BULBS / ELECTRONIC INDICATOR / LEDS", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[45] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "44", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK FUNCTION OF DOWN / UP COLLECTIVE SYSTEM", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[46] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "45", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK OPERATION OF DUPLEX SYSTEM(IF ANY)", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[47] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "46", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK LANDING RE-OPENING FUNCTION WITH LANDING PUSH BUTTON", ln=0, border=0, align='L')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[48] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "47", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK LANDING PUSH BUTTON / PUSH BUTTONS / REPLACE", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[49] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(20, 3, "OTHERS", ln=1, border=0, align='C')

    pdf.set_font('helvetica', '', 6)
    pdf.cell(20, 3, "48", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK LIFT OPERATING SYSTEM", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[50] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "49", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "LIGHTING IN MOTOR ROOM / CAR TOP / PIT", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[51] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "50", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "CHECK AND OPERATION / ARD SWITCH 'ON' (IF ANY)", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[52] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.cell(20, 3, "51", ln=0, border=0, align='C')
    pdf.cell(3, 3, "", ln=0, border=0, align='C')
    pdf.cell(119, 3, "ROOF TRAP DOOR / MOTOR ROOM LOCK", ln=0, border=0, align='L')
    pdf.cell(10, 3, "*", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    pdf.cell(10, 3, "", ln=0, border=0, align='C')
    if args[53] != 'Y':
        pdf.cell(10, 3, "", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"
    else:
        pdf.cell(10, 3, "X", ln=1, border=0, align='C') # PLACE "X" HERE IF CHECKLIST HAS A CORRESPONDING "X"

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(139, 5, "RECOMMENDATIONS OF PARTS REPLACEMENTS / REPAIRS :", ln=1, border=0, align='L')
    if args[54] == 'N':
        pdf.cell(190, 5, "", ln=1, border=1, align='L')  # Insert Recommendations here (151 Characters only)
    else:
        pdf.cell(190, 5, args[54], ln=1, border=1, align='L')  # Insert Recommendations here (151 Characters only)

    pdf.set_font('helvetica', 'B', 7)
    pdf.cell(190, 5, "S: EVERY SERVICE, 3M: JANUARY, APRIL, JULY, OCTOBER, 6M: FEBBRUARY, AUGUST, 12M: DECEMBER", ln=1, border=0, align='C')
    pdf.cell(19, 5, "REMARKS :", ln=1, border=0, align='L')
    if args[55] == 'N':
        pdf.cell(190, 5, "", ln=1, border=1, align='L')  # Insert Recommendations here (151 Characters only)
    else:
        pdf.cell(190, 5, args[55], ln=1, border=1, align='L')  # Insert Recommendations here (151 Characters only)

    pdf.set_font('helvetica', '', 28)
    pdf.cell(190, 5, "", ln=1, border=0, align='L')
    pdf.cell(68, 20, "", ln=0, border=1, align='C')    # Place Assignee's Signature in cell
    pdf.cell(54, 5, "", ln=0, border=0, align='L')
    pdf.cell(68, 20, "", ln=1, border=1, align='C')    # Place Client's Signature in cell

    pdf.set_font('helvetica', 'BU', 7)
    pdf.cell(32, 5, "Serviceman Name / Sign: ", ln=0, border=0, align='L')
    pdf.set_font('helvetica', 'U', 7)
    pdf.cell(36, 5, "", ln=0, border=0, align='L')  # Insert Assignee's name
    pdf.cell(54, 5, "", ln=0, border=0, align='L')
    pdf.set_font('helvetica', 'BU', 7)
    pdf.cell(25, 5, "Client Name / Sign: ", ln=0, border=0, align='L')
    pdf.set_font('helvetica', 'U', 7)
    pdf.cell(43, 5, "", ln=1, border=0, align='L')  # Insert Client's name

    pdf.set_font('helvetica', 'BU', 7)
    pdf.cell(32, 5, "Handover Date: ", ln=0, border=0, align='L')
    pdf.set_font('helvetica', 'U', 7)
    pdf.cell(36, 5, "", ln=0, border=0, align='L')  # Insert Handover date here
    pdf.cell(54, 5, "", ln=0, border=0, align='L')
    pdf.set_font('helvetica', 'BU', 7)
    pdf.cell(25, 5, "Acknowledge Date: ", ln=0, border=0, align='L')
    pdf.set_font('helvetica', 'U', 7)
    pdf.cell(43, 5, "", ln=1, border=0, align='L')   # Insert Client sign date here

    pdf.output('documents/' + args[0] + '.pdf') # Output to Documents in Dropbox
    pdf.close()

def add_sig2(track_no,  handover, ackdate):
    in_pdf_file = "documents/" + track_no + ".pdf"
    out_pdf_file = "documents/" + track_no + "sign.pdf"

    assgnee = "temp/" + track_no + "assgnee.png"
    client = "temp/" + track_no + "client.png"

    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.setFontSize(9)
    # can.drawString(0, 0, review)

    can.drawImage(assgnee, 70, 65, width=120, preserveAspectRatio=True, mask='auto')
    can.drawImage(client, 400, 65, width=120, preserveAspectRatio=True, mask='auto')
    can.drawString(100, 85, handover)
    can.drawString(450, 85, ackdate)
    can.showPage()

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    new_pdf = PdfFileReader(packet)

    # read the existing PDF
    f = open(in_pdf_file, "rb")
    existing_pdf = PdfFileReader(f)
    output = PdfFileWriter()

    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # page = existing_pdf.getPage(1)
    # page.mergePage(new_pdf.getPage(1))
    # output.addPage(page)

    outputStream = open(out_pdf_file, "wb")
    output.write(outputStream)
    outputStream.close()
    f.close()

    # file_from = 'documents/' + track_no + 'sign.pdf'
    # # API v2
    # flag = False
    # index = 1

    # while flag == False:
    #     if upload_file(track_no, file_from, index):
    #         flag = True
    #     else:
    #         index += 1


def sort_records(records):
    supadm_list = []
    adm_list = []
    usr_list = []

    for item in records:
        if item[8] == "SupAdm":
            supadm_list.append(item)
        if item[8] == "Admin":
            adm_list.append(item)
        if item[8] == "User":
            usr_list.append(item)

    sorted_list = supadm_list + adm_list + usr_list
    return sorted_list


def send_notif(name, track_no, phone):
    # account_sid = 'AC68cb4fdf764abcce1e0cef75b78d89e7'
    # auth_token = 'd6f351ab7c59e147e6b6630574bcfb15'
    client = Client(account_sid, auth_token)

    client.messages.create(
        from_='whatsapp:+14155238886',
        body='Hi %s,\n\nYou have a new work order - *S/No: %s*' % (name, track_no),
        to='whatsapp:+65' + phone
    )


def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def generate_token():
    char = 'abcdefghijklmnopqrstuvwxyz'
    num = '0123456789'

    length = 36
    token = ''

    switch = [char, num]
    for i in range(36):
            choice = switch[random.randint(0, 1)]
            token += choice[random.randint(0, len(choice) - 1)]

    return token


def tokenCleaning():
    db = shelve.open('resetToken.db', 'c')
    tokensDict = {}
    try:
        tokensDict = db["tokens"]
    except:
        pass
    tokensToPop = []
    for tokenID in tokensDict:
        if datetime.datetime.now() - tokensDict[tokenID][1] > datetime.timedelta(minutes = 5):
            tokensToPop.append(tokenID)
    for id in tokensToPop:
        tokensDict.pop(id)
    db["tokens"] = tokensDict
    db.close()


def resetPass(password, email):
    salt = ""
    hashed_password = generate_password_hash(password)

    sql_update = """ UPDATE User SET Salt = %s, Password = %s WHERE Email = %s"""
    args = (salt,hashed_password, email)

    cursor = connection.cursor()
    cursor.execute(sql_update,args)
    connection.commit()

def change_userid(username):
    sql_update = """UPDATE User SET UserID = '{}' WHERE Role = 'SvrAdm' """
    cursor.execute(sql_update.format(username))
    connection.commit()

def change_password(password):
    sql_update = """UPDATE User SET Password = '{}' WHERE Role = 'SvrAdm' """
    cursor.execute(sql_update.format(password))
    connection.commit()

with open('manage.txt', 'r') as file:
    lines = file.readlines()
    file.close()

mgr_salt = lines[0][0:-1]
mgr_salt = mgr_salt.encode('utf-8')

mgr_hash = lines[1][0:-1]
mgr_hash = mgr_hash.encode('utf-8')

def verify(userid, password):
        input_password =  password
        if check_password_hash(input_password, mgr_hash):
            user = User('0', 'svrmanager1', '', '', '', '', 'SvrMgr')
            login_user(user)
            return True
        else:
            return False

def change_exppass(credentials):
    salt = ""
    salt = salt.decode('utf-8')
    hashed_credentials = generate_password_hash(password.encode('utf-8'))


    hashed_credentials = hashed_credentials.decode('utf-8')

    lines = [salt, '\n'+hashed_credentials]
    with open('exp_pass.txt','w') as e:
        e.writelines(lines)
        e.close()
