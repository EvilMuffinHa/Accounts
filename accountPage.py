from flask import Flask
from flask import render_template
from flask import request, redirect
import sqlite3
import time

CASH_CARD = 'No Card (Cash)'
ERROR_CODE = {'account':[], 'view':[]}

#(year integer, month integer, date integer, pay text, card text, amount real,
#description text, category text)

app = Flask(__name__)

@app.route('/')
def account_page():
    if(len(ERROR_CODE['account']) == 0):
        return render_template("full.html")
    code = ERROR_CODE['account'][0]
    ERROR_CODE['account'].clear()
    return render_template("full.html", error=code)

@app.route('/newPurchase', methods=['POST'])
def new_purchase():
    ###Uses request to get the form answers for each field
    formNames = ['purchaseDate', 'type', 'cardName', 'amount', 'description', 'category']
    info = get_form_responses(formNames)
    errorCode = check_responses(info)
    if(errorCode):
        ERROR_CODE['account'].append(errorCode)
        return redirect('/')
    
    date, payType, cardName, amount = info[0], info[1], info[2], info[3]
    description, category = info[4], info[5]

    ###Gets the fields needed for the database from the form answers
    year, month, day = map(int, date.split('-'))
    amount = round(float(amount), 2)
    if(cardName == CASH_CARD):
        cardName = ''
        
    newRow = (year, month, day, payType, cardName, amount, description, category)
    insert_value(newRow)
    return redirect(request.referrer)

@app.route('/view')
def view_data():
    if(len(ERROR_CODE['view']) == 0): 
        return render_template("view.html")
    code = ERROR_CODE['view'][0]
    ERROR_CODE['view'].clear()
    return render_template("view.html", error=code)

@app.route('/chart', methods=['POST'])
def output_chart():
    startDate = request.form['startDate']
    endData = map(int, request.form['endDate'].split('-'))
    if(not(check_time(endData, startDate))):
        ERROR_CODE['view'].append('Start Date is after the End Date')
        return redirect('/view')

    ERROR_CODE['view'].append('Making chart for: ' + startDate + ' to ' + request.form['endDate'])
    return redirect(request.referrer)

def insert_value(value):
    conn = sqlite3.connect('accounts.db')
    c = conn.cursor()
    c.execute('''INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', value)
    conn.commit()
    conn.close()

def get_form_responses(formNames):
    info = ['']*len(formNames)
    for i in range(len(formNames)):
        info[i] = request.form[formNames[i]]
    return info

def check_responses(responses):
    if(responses[0] == ""):
        return "Wrong Date"
    
    nowTime = time.localtime()
    rowTime = (nowTime.tm_year, nowTime.tm_mon, nowTime.tm_mday)
    if(not(check_time(rowTime, responses[0]))):
        return "Date is After Today"
    if(responses[2] == ""):
        return "Wrong Card"

    if(not(check_float(responses[3]) and float(responses[3]) >= 0)):
        return "Wrong Amount"

    if(responses[-1] == ""):
        return "Wrong Category"
    return ""

def check_time(newTime, givenTime):
    gYear, gMonth, gDay = map(int, givenTime.split('-'))
    rYear, rMonth, rDay = newTime

    if(gYear > rYear):
        return False
    if(gYear < rYear):
        return True
    if(gMonth > rMonth):
        return False
    if(gMonth < rMonth):
        return True
    if(gDay > rDay):
        return False
    if(gDay < rDay):
        return True
    return True

def check_float(num):
    try:
        num = float(num)
        return True
    except ValueError:
        return False
