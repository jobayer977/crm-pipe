from flask import Flask, render_template, redirect, url_for, flash, make_response, session, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


from werkzeug.security import generate_password_hash, check_password_hash
import hmac, hashlib

from flask_wtf.csrf import CSRFProtect, CSRFError

from datetime import datetime, timedelta


import os
import base64, time

from extension.forms import *
from extension.functions import *

import smtplib
from email.message import EmailMessage

import googleapiclient
from googleapiclient.errors import HttpError

import shelve


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.update(
    SESSION_COOKIE_SECURE = False,
    SESSION_COOKIE_HTTPONLY= True,
    SESSION_COOKIE_SAMESITEB = 'Lax'
)

app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>


# sms_username = ""
# sms_token = ""
# client = TextmagicRestClient(sms_username, sms_token)



# connection = mysql.connector.connect(host='localhost',
#                                      database='wmodb',
#                                      user='root',
#                                      password='Aktusmu2019') ######### change accordingly

try:
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        mySql_Create_UserTable_Query = """CREATE TABLE IF NOT EXISTS User (
                             Id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                             UserID varchar (25) NOT NULL UNIQUE,
                             FName varchar(25) NULL,
                             LName varchar (25) NULL,
                             Phone varchar(8) NULL,
                             Password varchar(250) NOT NULL,
                             Salt varchar(250) NOT NULL,
                             Email varchar(60) NULL UNIQUE,
                             Role varchar(20) NOT NULL
                             ); """
        user_table = cursor.execute(mySql_Create_UserTable_Query)


        mySql_Create_OrderTable_Query = """CREATE TABLE IF NOT EXISTS `Order` (
                                Track_no varchar(7) NOT NULL PRIMARY KEY,
                                Category varchar(11) NOT NULL,
                                Assignee varchar(100) NOT NULL,
                                Date_assgn varchar(20) NOT NULL,
                                Time_assgn varchar(10) NOT NULL,
                                Caller varchar(100) NOT NULL,
                                Company_name varchar(100) NOT NULL,
                                Site_addr varchar(100) NOT NULL,
                                Date_rec varchar(20) NOT NULL,
                                Time_rec varchar(10) NOT NULL,
                                Complain varchar(1000) NOT NULL,
                                Special_inst varchar(1000) NOT  NULL,
                                Status varchar(1) NOT NULL,
                                EventId varchar(40) NOT NULL
                                );
                                """
        order_table = cursor.execute(mySql_Create_OrderTable_Query)

        mySql_Create_MaintenanceTable_Query = """CREATE TABLE IF NOT EXISTS Maintenance (
                                Track_no varchar(7) NOT NULL PRIMARY KEY ,
                                Category varchar(11) NOT NULL,
                                Assignee varchar(100) NOT NULL,
                                Date_assgn varchar(20) NOT NULL,
                                Time_assgn varchar(10) NOT NULL,
                                Company_name varchar(100) NOT NULL,
                                Site_addr varchar(100) NOT NULL,
                                Lift_type varchar(100) NOT NULL,
                                Other_Lift_Type varchar(100) NOT NULL,
                                Contract_type varchar(100) NOT NULL,
                                Other_Contract_Type varchar(100) NOT NULL,
                                Status varchar(1) NOT NULL,
                                EventId varchar(40) NOT NULL
                                );
                                """
        maintenance_table = cursor.execute(mySql_Create_MaintenanceTable_Query)

        mySql_Create_Caller_Desc_Table = """
                                CREATE TABLE IF NOT EXISTS Caller_Desc(
                                Track_no varchar(7) NOT NULL PRIMARY KEY,
                                Lift_no varchar(7) NOT NULL,
                                Breakdown varchar(1) NOT NULL ,
                                Mantrap varchar(1) NOT NULL ,
                                Lightfan varchar(1) NOT NULL ,
                                Travelnoise varchar(1) NOT NULL ,
                                Notlevelling varchar(1) NOT NULL ,
                                Buttonindicator varchar(1) NOT NULL ,
                                Others varchar(150) NOT NULL
                                );

        """
        callerdesc_table = cursor.execute(mySql_Create_Caller_Desc_Table)

        mySql_Create_Fault_Type_Table = """
                                CREATE TABLE IF NOT EXISTS Fault_Type(
                                Track_no varchar(7) NOT NULL PRIMARY KEY,
                                Lift_no varchar(7) NOT NULL,
                                 Falsecall varchar(1) NOT NULL ,
                                 Misuse varchar(1) NOT NULL ,
                                 Equipment_failure varchar(1) NOT NULL ,
                                 Power_failure varchar(1) NOT NULL ,
                                 Water_ingrees varchar(1) NOT NULL ,
                                 Vandalism varchar(1) NOT NULL ,
                                 Others varchar(150) NOT NULL
                                );

        """
        faulttype_table = cursor.execute(mySql_Create_Fault_Type_Table)


        mySql_Create_Fault_Details_Table = """
        CREATE TABLE IF NOT EXISTS Fault_Details(
                                    Track_no varchar(7) NOT NULL PRIMARY KEY,
                                    Lift_no varchar(7) NULL,
                                        Hydraulicdrive varchar(1) NOT NULL ,
                                        Hydraulicsys varchar(1) NOT NULL ,
                                        Hoistmachine varchar(1) NOT NULL ,
                                        `Landing/car_door` varchar(1) NOT NULL ,
                                        Landingstationcircuit varchar(1) NOT NULL ,
                                        `Light/fan_fitting` varchar(1) NOT NULL ,
                                        `Cartop/shaft_electrical` varchar(1) NOT NULL ,
                                        `Cartop/shaft_mechanical` varchar(1) NOT NULL ,
                                        `ard/ebops` varchar(1) NOT NULL ,
                                        Controller varchar(1) NOT NULL ,
                                        `Car_station/circuit` varchar(1) NOT NULL ,
                                        `Car_cage/counterweight` varchar(1) NOT NULL ,
                                        `Governor/safetygear` varchar(1) NOT NULL ,
                                        Offseal_leaking varchar(1) NOT NULL ,
                                        Securitysystem varchar(1) NOT NULL ,
                                        `Supervisor/lobbyvision` varchar(1) NOT NULL ,
                                     Others varchar(150) NOT NULL
                                    );

        """
        faultdetails_table = cursor.execute(mySql_Create_Fault_Details_Table)

        mySql_Create_Actions_Taken_Table = """
                                CREATE TABLE IF NOT EXISTS Actions_Taken(
                                Track_no varchar(7) NOT NULL PRIMARY KEY,
                                Lift_no varchar(7) NOT NULL,
                                  Required_serviced varchar(1) NOT NULL ,
                                  Replaced_parts varchar(1) NOT NULL ,
                                  Quotation_req varchar(1) NOT NULL ,
                                  Shutdown varchar(1) NOT NULL ,
                                  Tomonitor_followup varchar(1) NOT NULL ,
                                 Others varchar(150) NOT NULL
                                );

        """

        actionstaken_table = cursor.execute(mySql_Create_Actions_Taken_Table)

        mySql_Create_Desc_WorkDone_Table = """
                                CREATE TABLE IF NOT EXISTS Desc_Workdone(
                                Track_no varchar(7) NOT NULL PRIMARY KEY,
                                `Desc` varchar(1000) NOT NULL,
                                Completed varchar(1) NOT NULL,
                                Outstanding varchar(1) NOT NULL,
                                Others varchar(33) NOT NULL
                                );
        """
        desc_workdone = cursor.execute(mySql_Create_Desc_WorkDone_Table)

        mySql_Create_MaintenanceChecklist_Table = """
                                CREATE TABLE IF NOT EXISTS MaintenanceChecklist(
                                Track_no varchar(7) NOT NULL PRIMARY KEY,
                                Lift_no varchar(7) NOT NULL,
                                Date  varchar(10) NOT NULL,
                                `01` varchar(1) NOT NULL,
                                `02` varchar(1) NOT NULL,
                                `03` varchar(1) NOT NULL,
                                `04` varchar(1) NOT NULL,
                                `05` varchar(1) NOT NULL,
                                `06` varchar(1) NOT NULL,
                                `07` varchar(1) NOT NULL,
                                `08` varchar(1) NOT NULL,
                                `09` varchar(1) NOT NULL,
                                `10` varchar(1) NOT NULL,
                                `11` varchar(1) NOT NULL,
                                `12` varchar(1) NOT NULL,
                                `13` varchar(1) NOT NULL,
                                `14` varchar(1) NOT NULL,
                                `15` varchar(1) NOT NULL,
                                `16` varchar(1) NOT NULL,
                                `17` varchar(1) NOT NULL,
                                `18` varchar(1) NOT NULL,
                                `19` varchar(1) NOT NULL,
                                `20` varchar(1) NOT NULL,
                                `21` varchar(1) NOT NULL,
                                `22` varchar(1) NOT NULL,
                                `23` varchar(1) NOT NULL,
                                `24` varchar(1) NOT NULL,
                                `25` varchar(1) NOT NULL,
                                `26` varchar(1) NOT NULL,
                                `27` varchar(1) NOT NULL,
                                `28` varchar(1) NOT NULL,
                                `29` varchar(1) NOT NULL,
                                `30` varchar(1) NOT NULL,
                                `31` varchar(1) NOT NULL,
                                `32` varchar(1) NOT NULL,
                                `33` varchar(1) NOT NULL,
                                `34` varchar(1) NOT NULL,
                                `35` varchar(1) NOT NULL,
                                `36` varchar(1) NOT NULL,
                                `37` varchar(1) NOT NULL,
                                `38` varchar(1) NOT NULL,
                                `39` varchar(1) NOT NULL,
                                `40` varchar(1) NOT NULL,
                                `41` varchar(1) NOT NULL,
                                `42` varchar(1) NOT NULL,
                                `43` varchar(1) NOT NULL,
                                `44` varchar(1) NOT NULL,
                                `45` varchar(1) NOT NULL,
                                `46` varchar(1) NOT NULL,
                                `47` varchar(1) NOT NULL,
                                `48` varchar(1) NOT NULL,
                                `49` varchar(1) NOT NULL,
                                `50` varchar(1) NOT NULL,
                                `51` varchar(1) NOT NULL,
                                Recommendations varchar(115) NOT NULL,
                                Remarks varchar(115) NOT NULL
                                );
        """

        motorroom = cursor.execute(mySql_Create_MaintenanceChecklist_Table)


        print("Tables created")
        pwd="Aktusmu2019"
        hashed=generate_password_hash(pwd)

        sql_insert = """INSERT IGNORE INTO User (UserID, Password, Salt, Role)
                        VALUES ('serveradm1', %s, %s, 'SvrAdm'); """
        args = (hashed, adm_salt)
        cursor.execute(sql_insert,args)
        connection.commit()




except Error as e:
    print("Error while connecting to MySQL", e)



@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor(buffered=True)
    current_session = session['current']

    if current_session['role'] == 'SvrMgr':
        user = User(0,user_id,"","","","","SvrMgr")


    else:
        sql_select = "SELECT * FROM User WHERE Id = {}"
        cursor.execute(sql_select.format(user_id))

        records = cursor.fetchone()
        user = User(records[0], records[1], records[2], records[3], records[4],records[5], records[8])
    return user


@csrf.exempt
@app.route('/', methods=['GET','POST'])
def login():
    expiration_start = check_expiration()
    login_form = LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        userid = login_form.userid.data
        password = login_form.password.data

        if validate_user(userid, password) == True:
            return redirect('home')

    return render_template('login.html', login_form=login_form, expiration_start=expiration_start)


@csrf.exempt
@app.route('/register', methods=['GET','POST'])
def register():
    register_form = Register(request.form)
    if request.method == 'POST' and register_form.validate():
        register_form = Register(request.form)
        userid = register_form.userid.data
        fname = register_form.firstname.data
        lname = register_form.lastname.data
        email = register_form.email.data
        phone = register_form.phone.data
        password = register_form.password.data

        create_account(userid, fname, lname, phone, password, email)
        return redirect(url_for('login'))
    return render_template('register.html', register_form=register_form)

@login_required
@app.route('/permissions', methods=['GET','POST'])
def permissions():
    if check_expiration()  != "expired":
        if current_user.get_role() == 'SupAdm' or current_user.get_role() == "SvrAdm":
            sql_select = """SELECT * FROM User"""
            cursor = connection.cursor()
            cursor.execute(sql_select)
            records = cursor.fetchall()
            records = sort_records(records)

            role = current_user.get_role()
            current_id = current_user.get_userid()

            return render_template('permissions.html', records=records, role=role, current_id= current_id)
        elif current_user.get_role() == 'User':
            flash("You cannot access this page")
            return redirect(url_for('work_order'))
        else:
            flash("You cannot access this page")
            return redirect(url_for('home'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))


@login_required
@app.route('/editroles/<userid>', methods=['GET','POST'])
def editroles(userid):
    role = request.form['role-select']
    print(userid)
    sql_update = """ UPDATE User SET Role=%s WHERE UserID=%s """
    args = (role,userid)

    cursor = connection.cursor()
    cursor.execute(sql_update,args)

    connection.commit()

    return redirect(url_for('permissions'))


@login_required
@app.route('/unlock', methods=['GET','POST'])
def unlock():
    expiration_key = ExpKey(request.form)
    if check_password_hash(expiration_key.key.data, exp_hash):
        with open('config.txt', 'r') as config:
            lines = config.readlines()
            config.close()

        for i in lines:
            lines = i.strip().split(',')
            new_line = ''
            print(lines)
            count = 0
            for i in lines:

                if (i != '' and count < 12) and (count != 11 and count != 12):
                    new_line += i + ','
                    count += 1
                elif (i == '' and count < 12) or count == 12 or count == 13:
                    new_line += ','
                    count += 1
                else:
                    new_line += i
                    count += 1

            with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

        flash('Please reset expiration')
        return redirect(url_for('config'))
    else:
        flash('Wrong key entered')
        return redirect(url_for('home'))

@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    expiration_key = ExpKey(request.form)

    if current_user.get_role() != 'User' and current_user.get_role() != 'SvrMgr':
        if convention_choice == 'alnum':
            new_track_no = generate_alnum_track_no()
        if convention_choice == 'num':
            new_track_no = generate_num_track_no()
        current_date = get_current_date()

        role = current_user.get_role()

        sql_select = """ SELECT UserID From User WHERE Role = 'User' """
        connection.commit()
        cursor = connection.cursor()
        cursor.execute(sql_select)
        records = cursor.fetchall()
        expiration_status = check_expiration()

        return render_template('home.html', new_track_no= new_track_no, current_date=current_date, role=role, records=records, expiration_status=expiration_status, expiration_key=expiration_key)

    else:
        return redirect(url_for('work_order'))


@app.route('/home2',methods=['GET','POST'])
@login_required
def home2():
    expiration_key = ExpKey(request.form)

    if current_user.get_role() != 'User' and current_user.get_role() != 'SvrMgr':
        if convention_choice == 'alnum':
            new_track_no = generate_alnum_track_no2()
        if convention_choice == 'num':
            new_track_no = generate_num_track_no2()
        current_date = get_current_date()

        role = current_user.get_role()

        sql_select = """ SELECT UserID From User WHERE Role = 'User' """
        connection.commit()
        cursor = connection.cursor()
        cursor.execute(sql_select)
        records = cursor.fetchall()
        expiration_status = check_expiration()

        return render_template('home2.html', new_track_no= new_track_no, current_date=current_date, role=role, records=records, expiration_status=expiration_status, expiration_key=expiration_key)

    else:
        return redirect(url_for('work_order'))

@app.route('/future', methods=['GET','POST'])
@login_required
def future():
    return render_template('future.html')


@app.route('/createOrder', methods=['GET','POST'])
@login_required
def create_order():
    if check_expiration() != "expired":
        if current_user.get_role() != 'User' and current_user.get_role() != 'SvrMgr':
            if request.method == 'POST':
                category = request.form['category']
                print(category)
                if category == 'Call back':
                    datereceived = request.form['datereceived']
                    timereceived =request.form['timereceived']
                    caller = request.form['caller']
                    company = request.form['company']
                    complain = request.form['complain']
                    track_no = request.form['trackno']
                    assignee = request.form['assigned']
                    dateassigned = request.form['dateassigned']
                    timeassigned = request.form['timeassigned']
                    siteaddr = request.form['siteaddr']
                    instructions = request.form['instructions']
                elif category == 'Maintenance':
                    company = request.form['company']
                    lifttype = request.form['lifttype']
                    track_no = request.form['trackno']
                    assignee = request.form['assigned']
                    dateassigned = request.form['dateassigned']
                    timeassigned = request.form['timeassigned']
                    siteaddr = request.form['siteaddr']
                    contracttype = request.form['contracttype']
                    if lifttype == 'Others':
                        others1 = request.form['others1']
                    else:
                        others1 = 'None'
                    if contracttype == 'Others':
                        others2 = request.form['others2']
                    else:
                        others2 = 'None'
                else:
                    flash('Category not available')
                    return redirect(url_for('home'))

                # Inserting into the database
                cursor = connection.cursor(buffered=True)
                connection.commit()
                sql_select = """SELECT *  FROM User WHERE UserID = '{}' """
                cursor.execute(sql_select.format(assignee))
                records = cursor.fetchall()
                if records == []:
                    flash("The UserID that you have assigned to does not exist")
                    return redirect(url_for('home'))



                records = records[0]

                name = records[1]
                phone = records[4]
                emailaddr  = records[7]

                #send_notif(name,track_no,phone) ## whatsapp notifications

                # creates one hour event tomorrow 10 AM IST
                service = get_calendar_service()

                tomorrow = datetime.datetime(int(dateassigned[0:4]), int(dateassigned[5:7]), int(dateassigned[8:]))
                start = tomorrow.isoformat()

                event_result = service.events().insert(calendarId='primary',
                   body={
                       "summary": name + ', ' + track_no + ', ' + timeassigned,
                       "description": 'Assigned ' + name + ' to ' + siteaddr ,
                       "start": {"date": start[:10], "timeZone": 'Asia/Singapore'},
                       "end": {"date": start[:10], "timeZone": 'Asia/Singapore'},
                   }
                ).execute()

                event_id =  event_result['id']

                if category == 'Call back':
                    sql_insert = """INSERT INTO `Order` (Track_no, Category, Assignee, Date_assgn, Time_assgn, Caller, Company_name, Site_addr, Date_rec, Time_rec, Complain, Special_inst, Status, EventId)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                                        """
                    args= (track_no, category, assignee, dateassigned, timeassigned, caller, company, siteaddr, datereceived, timereceived, complain, instructions, 'N', event_id)
                    cursor.execute(sql_insert, args)
                    connection.commit()

                elif category == 'Maintenance':
                    sql_insert = """INSERT INTO Maintenance (Track_no, Category,Assignee,Date_assgn,Time_assgn,Company_name,Site_addr,Lift_type,Other_Lift_Type,Contract_type,Other_Contract_Type,Status, EventId)
                    VALUES (%s, %s , %s, %s ,%s ,%s , %s, %s, %s, %s, %s, %s, %s)
                    """
                    args= (track_no, category, assignee, dateassigned, timeassigned, company, siteaddr, lifttype, others1, contracttype, others2, 'N', event_id)
                    cursor.execute(sql_insert, args)
                    connection.commit()

                else:
                    pass

                # SENDER = "khongwka@gmail.com" ###### Put company Gmail here
                RECVR = emailaddr #### receiver here
                BODY = "Dear %s,\n\nYou have a new work order.\nPlease attend to it soon.\n\nThank you." % (records[2])


                msg = EmailMessage()
                msg.set_content(BODY)

                msg['Subject'] = 'No. %s - New Work Order' % (track_no)
                msg['From'] = SENDER
                msg['To'] = RECVR
                try:
                    # Send the message via our own SMTP server.
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(SENDER, GMAIL_PASS) #### replace password here
                    server.send_message(msg)
                    server.quit()
                    flash('Order Created Successfully!')
                    if category == "Call back":
                        return redirect(url_for('home'))
                    if category == "Maintenance":
                        return redirect(url_for('home2'))
                except:
                    flash('Order Created, but FAILED to inform worker. Please check if configurations are correct before creating work order.')
                    return redirect(url_for('config'))




            flash('Please fill up the form first')
            return redirect(url_for('home'))
        else:
            flash('You cannot access this page')
            return redirect(url_for('work_order'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('work_order'))




@app.route('/workOrder', methods=["GET","POST"])
@login_required
def work_order():
    if check_expiration() != "expired":
        if current_user.get_role() != 'SvrMgr':
            callorder_records=[]
            maintenance_records=[]
            try:
                current_session = session['current']
                current_userid = current_session['userid']
            except:
                flash('You have been logged out')
                return redirect(url_for('login'))

            cursor = connection.cursor()
            connection.commit()
            sql_select="""SELECT * FROM `Order` WHERE Assignee = '{}'; """
            cursor.execute(sql_select.format(current_userid))
            records = cursor.fetchall()
            for item in records:
                if item[12]=="N":
                    callorder_records.append(item)

            cursor = connection.cursor()
            connection.commit()
            sql_select="""SELECT * FROM Maintenance WHERE Assignee = '{}'; """
            cursor.execute(sql_select.format(current_userid))
            records = cursor.fetchall()
            for item in records:
                if item[11]=="N":
                    maintenance_records.append(item)

            return render_template('workorder.html', callorder_records=callorder_records, maintenance_records=maintenance_records)
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))


@login_required
@app.route('/checkList/<track_no>', methods=['GET','POST'])
def checklist(track_no):
    if current_user.get_role() != 'SvrMgr':
        cursor = connection.cursor()
        connection.commit()
        sql_select="""SELECT * FROM `Order` WHERE Track_No = '{}'; """
        cursor.execute(sql_select.format(track_no))
        records = cursor.fetchall()

        return render_template('checklist.html', current_order=records[0])
    else:
        flash('You cannot access this page')
        return redirect(url_for('credentials_unlocked'))

@login_required
@app.route('/checklist2/<track_no>', methods=['GET','POST'])
def checklist2(track_no):
    if current_user.get_role() != 'SvrMgr':
        cursor = connection.cursor()
        connection.commit()
        sql_select="""SELECT * FROM Maintenance WHERE Track_No = '{}'; """
        cursor.execute(sql_select.format(track_no))
        records = cursor.fetchall()

        return render_template('maintenance.html', current_order=records[0])
    else:
        flash('You cannot access this page')
        return redirect(url_for('credentials_unlocked'))

@login_required
@app.route('/creatingReport/<track_no>', methods=['GET','POST'])
def creatingreport(track_no):
    if check_expiration()  != "expired":
        if current_user.get_role != "SvrMgr":
            ## Caller Description
            caller_desc_key = ['liftno', 'breakdown', 'travelnoise','mantrap', 'notlevelling','lightfan','buttonindicator', 'others1']
            caller_desc_args = []

            ## Type of Fault
            type_of_fault_key = ['liftno', 'falsecall','powerfailure','misuse','wateringrees','equipmentfailure','vandalism', 'others2']
            type_of_fault_args = []

            ## Fault Details
            fault_details_key = ['liftno', 'hydraulicdrive', 'ARD/EBOPS','hydraulicsystem', 'controller','hoistmachine', 'carstationcircuit','landingcardoor', 'carcagecounterweight','landingstationcircuit', 'governorsafetycar','lightfanfitting', 'offsealleaking','cartopshaftelectrical', 'securitysystem', 'cartopshaftmechanical','supervisorylobbyvision','others3']
            fault_details_args = []

            ## Action Taken
            action_taken_key = ['liftno', 'requiredserviced','shutdown','replacedparts','tomonitorfollowup','quotationrequired', 'others4']
            action_taken_args = []

            ## Description of Work Done
            desc_key = ['description', 'completed', 'outstanding', 'others5']
            desc_args = []

            sections = [caller_desc_key, type_of_fault_key, fault_details_key, action_taken_key, desc_key]

            sql_insert_callerdesc = """INSERT INTO Caller_Desc (Track_no, Lift_no, Breakdown, Mantrap, Lightfan, Travelnoise, Notlevelling, Buttonindicator, Others) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            sql_insert_faulttype = """INSERT INTO Fault_Type (Track_no, Lift_no, Falsecall, Misuse, Equipment_failure, Power_failure, Water_ingrees, Vandalism, Others) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            sql_insert_faultdetails = """INSERT INTO Fault_Details (Track_no, Lift_no, Hydraulicdrive, Hydraulicsys, Hoistmachine, `Landing/car_door`, Landingstationcircuit, `Light/fan_fitting`, `cartop/shaft_electrical`, `cartop/shaft_mechanical`, `ard/ebops`, controller, `car_station/circuit`, `car_cage/counterweight`, `governor/safetygear`, offseal_leaking, securitysystem, `supervisor/lobbyvision`, Others) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            sql_insert_actiontaken = """INSERT INTO Actions_Taken (Track_no, Lift_no ,required_serviced, replaced_parts, quotation_req, shutdown, tomonitor_followup, others) VALUES (%s, %s, %s, %s, %s, %s, %s, %s )"""
            sql_insert_desc = """INSERT INTO Desc_WorkDone (Track_no, `Desc`, Completed, Outstanding, Others) VALUES (%s, %s, %s, %s, %s)"""

            cursor = connection.cursor()
            for item in sections:
                args=[track_no]
                for name in item:
                    if name in request.form:
                        if request.form[name] != '':
                            args.append(request.form[name])
                        else:
                            args.append("N")
                    else:
                        args.append("N")

                args = tuple(args)
                if item == caller_desc_key:
                    caller_desc_args = args
                    cursor.execute(sql_insert_callerdesc,args)
                if item == type_of_fault_key:
                    type_of_fault_args = args
                    cursor.execute(sql_insert_faulttype, args)
                if item == fault_details_key:
                    fault_details_args = args
                    cursor.execute(sql_insert_faultdetails, args)
                if item == action_taken_key:
                    action_taken_args = args
                    cursor.execute(sql_insert_actiontaken, args)
                if item == desc_key:
                    desc_args = args
                    cursor.execute(sql_insert_desc, args)

                sql_update_order = """UPDATE `order` SET status = 'Y' WHERE Track_no = '{}' """
                cursor.execute(sql_update_order.format(track_no))
                connection.commit()
            create_pdf(caller_desc_args,type_of_fault_args,fault_details_args,action_taken_args,desc_args)
            return redirect(url_for('sign', track_no=track_no))
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))

@login_required
@app.route('/creatingReport2/<track_no>', methods=['GET','POST'])
def creatingreport2(track_no):
    if check_expiration()  != "expired":
        if current_user.get_role != "SvrMgr":
            column_name = ''
            cursor = connection.cursor()
            sql_insert = """ INSERT INTO MaintenanceChecklist (Track_no, Lift_no, Date,  `01`, `02` , `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `23`, `24`, `25`, `26`
            , `27`, `28`, `29`, `30`, `31`, `32`, `33`, `34`, `35`, `36`, `37`, `38`, `39`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `48`, `49`, `50`, `51`, Recommendations, Remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
            args = [track_no]

            if request.form['liftno'] != '':
                args.append(request.form['liftno'])

            if request.form['date'] != '':
                args.append(request.form['date'])

            for i in range(1,52):
                if len(str(i)) == 1:
                    column_name = str('0')+ str(i)
                else:
                    column_name = str(i)
                if column_name in request.form:
                    if request.form[column_name] != '':
                        args.append('Y')
                else:
                    args.append('N')

            if request.form['recommendations'] != '':
                args.append(request.form['recommendations'])
            else:
                args.append('N')

            if request.form['remarks'] != '':
                args.append(request.form['remarks'])
            else:
                args.append('N')

            cursor.execute(sql_insert,args)
            sql_update = """UPDATE Maintenance SET Status = 'Y' WHERE Track_no = '{}' """
            cursor.execute(sql_update.format(track_no))
            connection.commit()

            sql_select = """SELECT * FROM Maintenance WHERE Track_no = '{}'"""
            cursor.execute(sql_select.format(track_no))
            records = cursor.fetchone()

            create_pdf2(args, records)
            return redirect(url_for('sign2', track_no=track_no))
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))

@login_required
@app.route('/sign/<track_no>',methods=['GET','POST'])
def sign(track_no):
    if check_expiration()  != "expired":
        if current_user.get_role() != "SvrMgr":
            current_date = get_current_date()
            return render_template('sign.html', track_no=track_no, current_date = current_date)
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))


@login_required
@app.route('/sign2/<track_no>',methods=['GET','POST'])
def sign2(track_no):
    if check_expiration()  != "expired":
        if current_user.get_role() != "SvrMgr":
            current_date = get_current_date()
            return render_template('sign2.html', track_no=track_no, current_date = current_date)
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))


@csrf.exempt
@login_required
@app.route('/processing', methods=['GET','POST'])
def processing():
    if check_expiration()  != "expired":
        if current_user.get_role() != "SvrMgr":
            output = request.get_json()
            track_no = output[0]
            assgnee = base64.b64decode(output[1])
            client = base64.b64decode(output[2])
            review = output[3]
            onsite = output[4]
            takeover = output[5]
            handover = output[6]
            timeout = output[7]

            with open("temp/"+track_no+"assgnee.png", "wb") as f:
                f.write(assgnee)
            with open("temp/"+track_no+"client.png", "wb") as fa:
                fa.write(client)


            add_sig(track_no,review,onsite, takeover, handover, timeout)
            # add_review(track_no,review)
            remove_oldpdf(track_no)

            sql_select = """SELECT EventID From `Order` WHERE Track_no = '{}' """
            connection.commit()
            cursor = connection.cursor()
            cursor.execute(sql_select.format(track_no))
            records = cursor.fetchall()
            event_id = records[0][0]


            # Delete the event
            service = get_calendar_service()
            try:
               service.events().delete(
                   calendarId='primary',
                   eventId= event_id,
               ).execute()
            except googleapiclient.errors.HttpError:
               print("Failed to delete event")

            print("Event deleted")

            return "Data sent"
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for("home"))

@csrf.exempt
@login_required
@app.route('/processing2', methods=['GET','POST'])
def processing2():
    if check_expiration()  != "expired":
        print(current_user.get_role())
        if current_user.get_role() != "SvrMgr":

            output = request.get_json()
            track_no = output[0]
            assgnee = base64.b64decode(output[1])
            client = base64.b64decode(output[2])
            handover = output[3]
            ackdate = output[4]


            with open("temp/"+track_no+"assgnee.png", "wb") as f:
                f.write(assgnee)
            with open("temp/"+track_no+"client.png", "wb") as fa:
                fa.write(client)


            add_sig2(track_no, handover, ackdate)
            # add_review(track_no,review)
            remove_oldpdf(track_no)

            sql_select = """SELECT EventId From Maintenance WHERE Track_no = '{}' """
            connection.commit()
            cursor = connection.cursor()
            cursor.execute(sql_select.format(track_no))
            records = cursor.fetchall()
            event_id = records[0][0]


            # Delete the event
            service = get_calendar_service()
            try:
               service.events().delete(
                   calendarId='primary',
                   eventId= event_id,
               ).execute()
            except googleapiclient.errors.HttpError:
               print("Failed to delete event")

            print("Event deleted")

            return "Data sent"
        else:
            flash('You cannot access this page')
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for("home"))

@app.route('/credentials', methods=['GET','POST'])
def credentials():
        login_form = LoginForm(request.form)
        username = login_form.userid.data
        password = login_form.password.data

        if request.method == 'POST' and login_form.validate():
            if verify(username,password) == True:
                session['current'] = {'userid': 'svrmanager1', 'role': 'SvrMgr'}
                return redirect(url_for('credentials_unlocked'))


            else:
                flash('Invalid UserID or Password')
                return redirect(url_for('credentials'))
        return render_template('credentials.html', login_form=login_form)


@login_required
@app.route('/credentials_unlocked', methods=['GET','POST'])
def credentials_unlocked():
    if check_expiration()  != "expired":
        try:
            current_session = session['current']
            current_role = current_session['role']
        except:
            flash('You have been logged out')
            return redirect(url_for('login'))

        if current_role == "SvrMgr":
            credentials_user = CredentialsUser(request.form)
            credentials_pass = CredentialsPassword(request.form)
            changeexpkey = ChangeExpKey(request.form)

            connection.commit()
            sql_select = ''' SELECT UserId FROM User WHERE Role="SvrAdm" ; '''
            cursor = connection.cursor()
            cursor.execute(sql_select)
            records = cursor.fetchall()
            current_username = records[0][0]


            return render_template('credentials_unlocked.html', credentials_user=credentials_user, credentials_pass=credentials_pass, changeexpkey = changeexpkey, current_username=current_username)
        else:
            flash('You cannot access this page')
            return redirect(url_for('home'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('login'))


@login_required
@app.route('/change_svradmusr', methods=['GET','POST'])
def change_svradmusr():
    credentials_user = CredentialsUser(request.form)
    if request.method == "POST" and credentials_user.validate():

        username = credentials_user.userid.data

        sql_select = """SELECT UserID FROM User WHERE UserID = '{}'"""
        connection.commit()
        cursor = connection.cursor()
        cursor.execute(sql_select.format(username))
        records = cursor.fetchall()

        if records == []:
            change_userid(username)
            flash('Credentials have been updated')
        else:
            flash('UserID is already in use')
            return redirect(url_for('login'))


@login_required
@app.route('/change_svradmpw', methods=['GET','POST'])
def change_svradmpw():
        credentials_pass = CredentialsPassword(request.form)
        if request.method == "POST" and credentials_pass.validate():
            password = credentials_pass.password.data
            confirm_passwd = credentials_pass.confirm_pass.data

            if password == confirm_passwd:
                connection.commit()
                sql_select = ''' SELECT UserId FROM User WHERE Role="SvrAdm" ; '''
                cursor = connection.cursor()
                cursor.execute(sql_select)
                records = cursor.fetchall()
                current_username = records[0][0]

                sql_select = """ SELECT Password, Salt FROM User WHERE UserID = '{}' """
                connection.commit()
                cursor = connection.cursor()
                cursor.execute(sql_select.format(current_username))
                records = cursor.fetchone()

                salt = records[1].encode('utf-8')

             # hash the password using the salt
                input_password_hash = generate_password_hash(password)

# convert the hashed password to string (if needed)
                input_password_hash = input_password_hash.decode('utf-8')

                change_password(input_password_hash)
                flash('Credentials have been updated')

            else:
                flash('Passwords do not match, try again')

            return redirect(url_for('credentials_unlocked'))

@login_required
@app.route('/change_expkey', methods=['GET','POST'])
def change_expkey():
        changeexpkey = ChangeExpKey(request.form)
        if request.method == "POST" and changeexpkey.validate():
            if changeexpkey.password.data == changeexpkey.confirm_pass.data:
                change_exppass(changeexpkey.password.data)
                flash('Credentials have been updated')
            else:
                flash('Keys do not match. Try again.')

            return redirect(url_for('credentials_unlocked'))

@login_required
@app.route('/config', methods=['GET','POST'])
def config():
    if check_expiration() != "expired":
        try:
            current_session = session['current']
            current_role = current_session['role']
        except:
            flash('You have been logged out')
            return redirect(url_for('login'))
        if current_user.get_role() != "SvrMgr":
            if current_role == 'SvrAdm':
                tracknoconv_form = TrackNoConv(request.form)
                tracknolen_form = TrackNoLen(request.form)
                tracknoalpha_form = TrackNoAlpha(request.form)
                tracknostart_form = TrackNoStart(request.form)
                tracknoconv2_form = TrackNoConv2(request.form)
                tracknolen2_form = TrackNoLen2(request.form)
                tracknoalpha2_form = TrackNoAlpha2(request.form)
                tracknostart2_form = TrackNoStart2(request.form)

                emailnotif_form = EmailNotif(request.form)
                emailtoken_form = EmailToken(request.form)
                twiliosid_form = TwilioSID(request.form)
                twiliotoken_form = TwilioToken(request.form)
                expcounterstart_form = ExpCounterStart(request.form)
                expcounterperiod_form = ExpCounterPeriod(request.form)

                with open('config.txt','r') as f:
                    lines = f.readlines()
                    f.close()

                for i in lines:
                    lines = i.strip().split(',')

                if request.method == 'POST' and tracknoconv_form.validate():
                    value = tracknoconv_form.convention.data

                    lines[0] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))


                if request.method == 'POST' and tracknolen_form.validate():

                    value = tracknolen_form.len_trackno.data
                    print('hits')
                    print(value)
                    print(tracknolen2_form.len_trackno2.data)
                    lines[1] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))

                if request.method == "POST" and tracknostart_form.validate():
                    value = str(tracknostart_form.starting_no.data)
                    if len(value) > digits:
                        flash("Starting No must have less digits than the Length of Tracking No")
                        return redirect(url_for('config'))
                    lines[2] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','


                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()


                if request.method == 'POST' and tracknoalpha_form.validate():
                    value = tracknoalpha_form.leading_alpha.data

                    lines[3] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))

                if request.method == 'POST' and tracknoconv2_form.validate():
                    value = tracknoconv2_form.convention2.data

                    lines[4] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))


                if request.method == 'POST' and tracknolen2_form.validate():
                    print('hits')

                    value = tracknolen2_form.len_trackno2.data
                    print(value)
                    lines[5] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))

                if request.method == "POST" and tracknostart2_form.validate():
                    value = str(tracknostart2_form.starting_no2.data)
                    if len(value) > digits:
                        flash("Starting No must have less digits than the Length of Tracking No")
                        return redirect(url_for('config'))
                    lines[6] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','


                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()


                if request.method == 'POST' and tracknoalpha2_form.validate():
                    value = tracknoalpha2_form.leading_alpha2.data

                    lines[7] = value

                    new_line = ''
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))

                if request.method == 'POST' and emailnotif_form.validate():
                    value = emailnotif_form.email.data

                    new_line = ''
                    lines[8] = value
                    lines = list(filter(None,lines))
                    remain = 14 - len(lines)

                    for item in lines:
                        if lines[-1] == item:
                            new_line += item
                        else:
                            new_line += item + ','

                    if remain > 0 :
                        for i in range(remain):
                                new_line += ','

                    with open('config.txt','w') as f:
                        f.write(new_line)
                        f.close()

                    return redirect(url_for('config'))

                if request.method == 'POST' and emailtoken_form.validate():
                    value = emailtoken_form.token.data

                    new_line = ''

                    lines[9] = value
                    count = 0
                    for i in lines:

                        if i != '' and count < 13:
                            new_line += i + ','
                            count += 1
                        elif i == '' and count < 13:
                            new_line += ','
                            count += 1
                        else:
                            new_line += i
                            count += 1

                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()

                    return redirect(url_for('config'))

                if request.method == 'POST' and twiliosid_form.validate():
                    value = twiliosid_form.account_sid.data
                    new_line = ''

                    lines[10] = value
                    count = 0
                    print(lines)
                    for i in lines:

                        if i != '' and count < 13:
                            new_line += i + ','
                            count += 1
                        elif i == '' and count < 13:
                            new_line += ','
                            count += 1
                        else:
                            new_line += i
                            count += 1

                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()

                if request.method == 'POST' and twiliotoken_form.validate():
                    value = twiliotoken_form.auth_token.data
                    new_line = ''

                    lines[11] = value
                    count = 0
                    for i in lines:

                        if i != '' and count < 13:
                            new_line += i + ','
                            count += 1
                        elif i == '' and count < 13:
                            new_line += ','
                            count += 1
                        else:
                            new_line += i
                            count += 1

                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()

                if request.method == "POST" and expcounterstart_form.validate():
                    value = str(expcounterstart_form.start.data)
                    new_line = ''

                    lines[12] = value
                    count = 0
                    for i in lines:

                        if i != '' and count < 13:
                            new_line += i + ','
                            count += 1
                        elif i == '' and count < 13:
                            new_line += ','
                            count += 1
                        else:
                            new_line += i
                            count += 1

                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()

                if request.method == "POST" and expcounterperiod_form.validate():
                    years = str(expcounterperiod_form.years.data)
                    months = str(expcounterperiod_form.months.data)
                    days = str(expcounterperiod_form.days.data)

                    value = years + '-' + months + "-" + days
                    new_line = ''

                    lines[13] = value
                    count = 0

                    for i in lines:
                        print(i)
                        print(count)
                        if i != '' and count < 13:
                            new_line += i + ','
                            count += 1
                        elif i == '' and count < 13:
                            new_line += ','
                            count += 1
                        else:
                            new_line += i
                            count += 1

                    with open('config.txt','w') as f:
                                f.write(new_line)
                                f.close()



                return render_template('config.html', tracknolen_form= tracknolen_form, tracknoconv_form=tracknoconv_form, tracknoalpha_form=tracknoalpha_form,  tracknolen2_form= tracknolen2_form, tracknoconv2_form=tracknoconv2_form, tracknoalpha2_form=tracknoalpha2_form,tracknostart2_form=tracknostart2_form, emailnotif_form=emailnotif_form,
                                       emailtoken_form=emailtoken_form, twiliosid_form=twiliosid_form, twiliotoken_form=twiliotoken_form, expcounterstart_form=expcounterstart_form,expcounterperiod_form=expcounterperiod_form,tracknostart_form=tracknostart_form,lines=lines)
            else:
                flash('You cannot access this page')
                return redirect(url_for('home'))
        else:
            return redirect(url_for('credentials_unlocked'))
    else:
        flash('Application needs to be reactivated')
        return redirect(url_for('home'))

@app.route('/forgotPassword', methods=['GET','POST'])
def forgotpassword():
    forgotpassForm = ForgotPass(request.form)
    userid = forgotpassForm.username.data
    tokenCleaning()
    if request.method == 'POST' and forgotpassForm.validate():
        db = shelve.open('resetToken.db')

        tokensDict = {}
        try:
            tokensDict = db["tokens"]
        except:
            pass

        sql_select = """SELECT Email FROM User WHERE UserID = '{}' """
        connection.commit()
        cursor = connection.cursor()
        cursor.execute(sql_select.format(userid))
        records = cursor.fetchone()
        token = generate_token()

        print(records)
        if records != None:
            user_email = records[0]

            url = request.base_url + "/" + token
            msg = EmailMessage()
            msg['Subject'] = 'Change Password'
            msg['From'] = SENDER
            msg['To'] = user_email
            msg.set_content(f"This is the link to reset your password:{url}")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login("khongwka@gmail.com", "tgnavilnivubbhlm")
                        smtp.send_message(msg)

            tokensDict[token] = [user_email, datetime.datetime.now()]
            db['tokens'] = tokensDict

            db.close()

            flash("A confirmation email has been sent to the email registered with the UserID for password reset")
        else:
            flash('This UserID has not been registered')

    return render_template('forgotpass.html', forgotpassForm = forgotpassForm)


@app.route('/forgotPassword/<token>', methods=['GET','POST'])
def resetpassword(token):
    resetpassForm = ResetPass(request.form)
    db = shelve.open('resetToken.db')
    tokensDict = {}

    try:
        tokensDict = db["tokens"]
    except:
        flash("Invalid or expired password reset link", "errors")
        return redirect(url_for("login"))

    if token in tokensDict:
        emailaddr = (tokensDict[token])[0]
        if request.method == 'POST' and resetpassForm.validate():
            if resetpassForm.confirm_pass.data == resetpassForm.password.data:
                resetPass(resetpassForm.confirm_pass.data, emailaddr)
                flash("Password has been reset")
                return redirect(url_for('login'))
        return render_template('resetpass.html', resetpassForm = resetpassForm)

    else:
        flash('Invalid Token')
        return redirect(url_for('home'))


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    session.pop('current')
    flash('You have been logged out')
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Please log in to access this page', 'danger')
    return redirect(url_for('login'))

@app.errorhandler(CSRFError)
def handle_csrf_error(e): #if user dont have csrf token or session has expired, this will run
    flash('Please log in to access this page', 'danger')
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host="0.0.0.0",  port=port)
