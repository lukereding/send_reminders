import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import smtplib
import os
import sys
import argparse
import plivo
import requests

''''

Python3 script that retreives a google sheet and emails people in the morning to remind them to go to BFL.

path to interpreter: /Users/lukereding/anaconda2/envs/google_sheets3/bin/python

needs an environmental variable called 'gmail' with the gmail password

executed as a cron job daily
/Users/lukereding/anaconda2/envs/google_sheets3/bin/python reminder_bfl.py
'''

def get_date():
    """Get today's date in the right format"""
    date = time.strftime('%d %B %Y')
    return date

def login_to_sheets():
    """Log in to google sheets via API and get the spreadsheet"""
    # use creds to create a client to interact with the Google Drive API
    if os.path.exists('/Users/lukereding/Downloads/secret_key.json):
        p = '/Users/lukereding/Downloads/secret_key.json
    else:
        p = './secret_key.json'
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(p, scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("BFL daily checks").sheet1
    return sheet

def get_quote():
    url = 'http://api.forismatic.com/api/1.0/'
    data = {
      'method' : 'getQuote',
      'format': 'text',
      'lang' :'en',
      'format': 'text'
    }
    response = requests.post(url, data=data)
    return(str(response.text))

def send_email(email_addr, name, password):
    """Send reminder emails to everyone in dict_of_recipients."""
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    quote = get_quote()
    try:
        smtpObj.login('lukereding@gmail.com', password)
    except:
        print("could not log in")

    # send the email
    smtpObj.sendmail('lukereding@gmail.com', email_addr, "Subject: BFL daily inspection reminder\nHey {name},\n\nJust a reminder that you're on duty for doing the BFL daily check today.\n\nOnce you complete the check, please fill out the form here: https://docs.google.com/a/utexas.edu/forms/d/e/1FAIpQLSdY-Tb-0UcYn03EZc0dWssTJQjYccAnnPfNXquLH-jsAku8ww/viewform?c=0&w=1.\n\nThe guidelines for doing the inspectations can be found here: https://github.com/lukereding/cummings_lab_members/blob/master/current-members/bfl_daily_checklist.md\n\nThanks a lot!\n\nLuke\n\n\n\n{quote}".format(name = name, quote = quote))

    print("email sent to {}".format(name))

def get_email_address(name):
    # define dict to store email addresses
    email_addresses = {'Luke': 'lukereding@utexas.edu',
                        'Kelly': 'kwallace@utexas.edu',
                        'Sarah': 'sarah.price@utmail.utexas.edu',
                        'Adam': 'adamredmer@hotmail.com',
                        'Parrish': 'scorpionjeger@hotmail.com',
                        'Mary': 'mramsey@austin.utexas.edu',
                        'Daniel': 'danielhauser77@gmail.com',
                        'Lily': 'lily.anastacia@gmail.com',
                        'Caleb': 'cnfleischer@gmail.com',
                        'Marisa': 'marisafajardo97@gmail.com'}
    if name not in email_addresses:
        sys.exit('email address for {} not found.'.format(name))
    else:
        return email_addresses[name]

if __name__ == '__main__':

    # get today's date
    date = get_date()

    # get the google sheet
    sheet = login_to_sheets()

    # find the correct rows
    row = [i for i, x in enumerate(sheet.col_values(1)) if x == date]

    # python starts at 0, google sheets starts at 1
    row = row[0] + 1

    # find out who is supposed to do the check
    on_duty = sheet.cell(row, 2).value

    # we don't need to bug tony
    if on_duty == 'Tony':
        print('No need to email Tony.')
        sys.exit(0)

    addr = get_email_address(on_duty)

    p = os.environ['gmail']

    try:
        send_email(addr, on_duty, p)
        print("email sent.")
    except:
        print("Unexpected error:" + str(sys.exc_info()))
        print("some or all emails were not sent.")
