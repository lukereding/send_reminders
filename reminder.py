import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import smtplib
import os
import sys

''''

Python script that retreives a google sheet, finds who hasn't done water changes, then sends them a reminder email.

path to interpreter: /Users/lukereding/anaconda2/envs/google_sheets/bin/python

needs an environmental variable called 'gmail' with the gmail password
'''


def get_date():
    '''Get today's date in the right format'''
    date = time.strftime('%d %B %Y')
    return date

def login_to_sheets():
    '''Log in to google sheets via API and get the spreadsheet'''
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/lukereding/Downloads/secret_key.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("water changes summer 2017").sheet1
    return sheet

def send_email(dict_of_recipients, password):
    '''Send reminder emails to everyone in dict_of_recipients.'''
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    try:
        smtpObj.login('lukereding@gmail.com', password)
    except:
        print("could not log in")
        # sys.exit(1)
    # send the emails
    for name, email in dict_of_recipients.iteritems():
        smtpObj.sendmail('lukereding@gmail.com', email, "Subject: water changes this week\nHey {},\n\nJust a reminder that you are on water change duty this week. Check the lab wiki for more information on water changes, rank assignments, how to sign off once you've done you water changes.\n\nYou can access the wiki here: https://github.com/lukereding/cummings_lab_members/tree/master/current-members. \n\nThanks a lot--\n\nLuke\n\n".format(name))
        print("email sent to {}".format(name))

if __name__ == '__main__':
    # define dict to store email addresses
    email_addresses = {'Luke': 'lukereding@utexas.edu', 'Kelly': 'kwallace@utexas.edu', 'Sarah': 'sarah.price@utmail.utexas.edu'}

    # define some acceptable responses in the form. All others will be considered uncompleted
    acceptable_responses = ['done', 'yes', 'finished', 'complete', 'completed', 'changed']

    # gt today's dat
    date = get_date()

    # get the google sheet
    sheet = login_to_sheets()

    # find the correct rows
    rows = [i for i, x in enumerate(sheet.col_values(1)) if x == date]

    # python starts at 0, google sheets starts at 1
    rows = [x + 1 for x in rows]

    # create an empty dict of people to email
    to_email = {}

    # find out who hasn't been doing their water changes
    for row in rows:
        # if they haven't done their water change
        if sheet.cell(row, 4).value.lower() not in acceptable_responses:
            # to_email.append(sheet.cell(row, 3).value)
            to_email[sheet.cell(row, 3).value] = email_addresses[sheet.cell(row, 3).value]

    p = os.environ['gmail']

    # send the emails
    try:
        send_email(to_email, p)
        print("emails sent")
    except:
        print("some or all emails were not sent.")
    sys.exit("everything worked.")
