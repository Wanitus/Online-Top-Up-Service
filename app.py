from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, app, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tdg_database.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)


# TODO 1 create database
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


# Route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Username or Password. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    txt = None
    txt_fname = None
    txt_lname = None
    if request.method == 'POST':
        if request.form['MobileNo'] != '':
            mn = request.form['MobileNo']
            mn = int(mn)
            # no_lst = lst
            if mn in lst:
                txt = str(mn)
                txt_fname = i["fname"]
                txt_lname = i["lname"]
            else:
                txt = 'Sorry Mobile Number : ' + str(mn) + ' Not Found !!!'
        else:
            return render_template('verify.html', notfound='Please Insert Mobile Number')
    return render_template('verify.html', check=txt, fname=txt_fname, lname=txt_lname)


@app.route('/notify', methods=['GET', 'POST'])
def notify():
    # if request.method == 'POST':
    #     return redirect(url_for('top_up'))
    #     # print(request.form['mobile_no'])
    #
    # # show the form, it wasn't submitted
    # return render_template('notify.html')
    mn_txt = None
    am_txt = None
    td_date = datetime.today().strftime('%d/%m/%Y')
    td_time = datetime.today().strftime('%H:%M:%S')
    if request.method == 'POST':
        if request.form['MobileNo'] != '':
            mn = request.form['MobileNo']
            mn = int(mn)
            if mn in lst:
                mn_txt = str(mn)
                am_txt = request.form['amount']
                ct = 0
                for i in data:
                    # print(i["trans_id"])
                    ids = i["cust_no"]
                    ct = ct + 1
                    if ids == mn:
                        # print(ct)
                        topup = int(am_txt)
                        print('Top-Up Cust_No: ' + str(mn) + 'Amount: ' + str(topup))
                        amount = i["amount"] + topup
                        sheet.update_cell(ct + 1, 8, amount)
                        sheet.update_cell(ct + 1, 4, td_date)
                        sheet.update_cell(ct + 1, 5, td_time)
                        mesg_type = 'Notify'
                        trans_id = i["cust_no"]
                        # TODO Keep Transaction
                        mesg_type = 'Notify'
                        trans_id = i["cust_no"]
                        send_date = td_date
                        send_time = td_time
                        service_code = 'TMNTOPUP'
                        cust_no = i["cust_no"]
                        amount_tp = topup
                        new_trans = TopUp(mesg_type=mesg_type,
                                          trans_id=trans_id,
                                          send_date=send_date,
                                          send_time=send_time,
                                          service_code=service_code,
                                          cust_no=cust_no,
                                          amount=amount_tp
                                          )
                        db.session.add(new_trans)
                        db.session.commit()

            else:
                mn_txt = 'Sorry ' + str(mn) + ' Not Found !!!'
        else:
            return render_template('notify.html', notfound='Please Insert Mobile Number')
    return render_template('notify.html', mobile=mn_txt, amount=am_txt, td_date=td_date, td_time=td_time)


#
# @app.route('/top_up')
# def top_up():
#     return render_template('top_up.html')


# TODO Create Data Model
class TopUp(db.Model):
    __tablename__ = 'TopUp'
    top_up_id = Column(Integer, primary_key=True)
    mesg_type = Column(String)
    trans_id = Column(String)
    send_date = Column(String)
    send_time = Column(String)
    service_code = Column(String)
    cust_no = Column(String)
    amount = Column(Float)


# TODO API to Google Sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("doc_name").sheet1
data = sheet.get_all_records()

# print(data)
maxrow = len(data) + 1
lst = []
for i in data:
    # print(i["trans_id"])
    ids = i["cust_no"]
    lst.append(ids)

if __name__ == '__main__':
    app.run(debug=True)
