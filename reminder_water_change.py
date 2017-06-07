import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import smtplib
import os
import sys
import argparse
import plivo
import requests
from email.mime.text import MIMEText
import datetime

''''

Python3 script that retreives a google sheet, finds who hasn't done water changes, then sends them a reminder email with a not quotations.

path to interpreter: /Users/lukereding/anaconda2/envs/google_sheets3/bin/python

needs an environmental variable called 'gmail' with the gmail password and various PLIVO variables to access the PLIVO API to send texts
'''

def get_old_date(number_days_ago):
    old_date = datetime.date.today() - datetime.timedelta(number_days_ago)
    date = old_date.strftime('%d %B %Y')
    return date

def get_mondays_date():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    monday = monday.strftime('%d %B %Y')
    return monday

def get_date():
    """Get today's date in the right format"""
    date = time.strftime('%d %B %Y')
    return date

def login_to_sheets():
    """Log in to google sheets via API and get the spreadsheet"""
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/lukereding/Downloads/secret_key.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("water changes summer 2017").sheet1
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

def send_email(dict_of_recipients, password):
    """Send reminder emails to everyone in dict_of_recipients."""
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    try:
        session.login('lukereding@gmail.com', password)
    except:
        print("could not log in")
        # sys.exit(1)
    # send the emails
    for name, [email, rack] in dict_of_recipients.items():
        # if it's monday, just send a 'letting you know' message
        if datetime.datetime.today().weekday() == 0:
            msg = MIMEText("""
Hey {name},

Congrats! You're on water change duty this week!

You have been assigned rack {rack} this week.

You can access the lab wiki for more information about water changes here: 
https://github.com/lukereding/cummings_lab_members/tree/master/current-members.

Be sure to sign off when you're done here:
https://docs.google.com/spreadsheets/d/1pVwqyetFLGVl_2qQ40qCH0Nvhe7ODzKC7J_oyQsiOQg/edit?usp=sharing.

And remember, come to one of the lab veterans with any questions you have.

Thanks!

Luke




{quote}""".format(rack = rack, name = name, quote = get_quote()))
        # otherwise
        else:
            msg = MIMEText("""
Hey {name},

Just a reminder that you are on water change duty this week. Water changes should be completed by the end of the week. Check the lab wiki for more information on water changes. You can access the wiki here: 

https://github.com/lukereding/cummings_lab_members/tree/master/current-members.

As a reminder, you have been assigned rack {rack} this week.

Be sure to sign off when you're done here:
https://docs.google.com/spreadsheets/d/1pVwqyetFLGVl_2qQ40qCH0Nvhe7ODzKC7J_oyQsiOQg/edit?usp=sharing.

Thanks a lot--

Luke




{quote}""".format(rack = rack, name = name, quote = get_quote()))
        msg['Subject'] = u'\U0001F514' + ' water changes this week'
        msg['From'] = 'info@lreding.com'
        msg['To'] = email
        msg = msg.as_string()

        # send the email
        session.sendmail('lukereding@gmail.com', email, msg)
        print("email sent to {}".format(name))

def send_text(dict_of_recipients, auth_id, token):
    """Sends text messages, logging when the text was not sent."""

    p = plivo.RestAPI(auth_id, token)

    for name, number in dict_of_recipients.items():
        print("sending text to {}".format(name))
        params = {
            'src': plivo_number,
            'dst' : number,
            'text' : "Hi {}, just a reminder that you have water changes this week that you have either not done or not signed off on. Thanks!".format(name),
            'method' : 'POST'
        }
        response = p.send_message(params)
        # check to make sure it's 202?

def parse_arguments():
    """Parse arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", help="Send email to those that have not done water changes?", action = "store_true")
    parser.add_argument("-t", "--text", help="Send text message to those that have not done water changes?", action = "store_true")
    args = parser.parse_args()
    return args.email, args.text

if __name__ == '__main__':

    email, text = parse_arguments()
    print("email: {}\ntext: {}".format(email, text))

    # define some acceptable responses in the form. All others will be considered uncompleted
    acceptable_responses = ['done', 'yes', 'yes?','finished', 'complete', 'completed', 'changed', 'yeah', 'yea', 'yep']

    # get monday's date
    date = get_mondays_date()

    # get the google sheet
    sheet = login_to_sheets()

    # find the correct rows
    rows = [i for i, x in enumerate(sheet.col_values(1)) if x == date]

    # python starts at 0, google sheets starts at 1
    rows = [x + 1 for x in rows]

    if email:
        # define dict to store email addresses
        email_addresses = {'Luke': 'lukereding@utexas.edu',
                            'Kelly': 'kwallace@utexas.edu',
                            'Sarah': 'sarah.price@utmail.utexas.edu',
                          'Jennifer': 'jschlauch@utexas.edu',
                          'Marisa': 'marisafajardo97@gmail.com',
                          'Lily': 'lily.anastacia@gmail.com',
                          'Daniel': 'danielhauser77@gmail.com',
                          'Huynh': 'huynhpham100@yahoo.com',
                          'Caleb': 'cnfleischer@gmail.com',
                          'Adam': 'adamredmer@hotmail.com'}

        # create an empty dict of people to email
        to_email = dict()

        # find out who hasn't been doing their water changes
        for row in rows:
            # if they haven't done their water change
            if sheet.cell(row, 4).value.lower() not in acceptable_responses:
                # to_email.append(sheet.cell(row, 3).value)
                to_email[sheet.cell(row, 3).value] = [email_addresses[sheet.cell(row, 3).value], sheet.cell(row, 2).value]

        p = os.environ['gmail']

        # pdb.set_trace()

        # send the emails
        try:
            send_email(to_email, p)
            print("emails sent")
        except:
            print("Unexpected error:" + str(sys.exc_info()))
            print("some or all emails were not sent.")

        # if texts are to be sent:
    if text:
        to_text = dict()
        phone_numbers = {'Luke': '+12406788175',
                        'Kelly': '+1231231234',
                        'Sarah': '+1231231234'}
        for row in rows:
            if sheet.cell(row, 4).value.lower() not in acceptable_responses:
                # to_email.append(sheet.cell(row, 3).value)
                to_text[sheet.cell(row, 3).value] = phone_numbers[sheet.cell(row, 3).value]

        plivo_number = os.environ.get('plivo_number')
        auth_id = os.environ.get('PLIVO_ID')
        token = os.environ.get('PLIVO_TOKEN')

        # try sending the texts
        if token and auth_id:
            try:
                send_text(to_text, auth_id, token)
                print("texts sent.")
            except:
                print("some or all texts were not sent.")
        else:
            print("problem assigning env variables")

    sys.exit("everything worked.")
