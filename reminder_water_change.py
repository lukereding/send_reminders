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
import re

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
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/{}/Downloads/secret_key.json'.format(os.environ["USER"]), scope)
    client = gspread.authorize(creds)
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("water changes Fall 2017").sheet1
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

def send_email(info, password):
    """Send reminder emails to everyone in dict_of_recipients."""
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    try:
        session.login('lukereding@gmail.com', password)
    except:
        print("could not log in")
        sys.exit(1)
    # send the emails
    for email, x in info.items():
        # parse items
        name = x[0][0]
        racks = x[1]
        shelves = x[2]

        todo = ""
        for i, rack in enumerate(racks):
            todo += "rack " + str(shelves[i]) + ", " + str(rack) + "\n"

        if datetime.datetime.today().weekday() == 0:
            msg = MIMEText("""
Hey {name},

Congratulations are in order: you're on water change duty this week! Water changes should be completed by the end of the week. Check the lab wiki for more information on water changes. You can access the wiki here:

https://github.com/lukereding/cummings_lab_members/tree/master/current-members.

This week you've been assigned:

{todo}

Be sure to sign off when you're done here:
https://docs.google.com/spreadsheets/d/1pVwqyetFLGVl_2qQ40qCH0Nvhe7ODzKC7J_oyQsiOQg/edit?usp=sharing.

Thanks a lot--

Luke




{quote}""".format(todo = todo, name = name, quote = get_quote()))
        # otherwise
        else:
            msg = MIMEText("""
Hey {name},

Just a reminder that you are on water change duty this week. Water changes should be completed by the end of the week. Check the lab wiki for more information on water changes. You can access the wiki here:

https://github.com/lukereding/cummings_lab_members/tree/master/current-members.

Tanks that still need to be water changed:

{todo}

Be sure to sign off when you're done here:
https://docs.google.com/spreadsheets/d/1pVwqyetFLGVl_2qQ40qCH0Nvhe7ODzKC7J_oyQsiOQg/edit?usp=sharing.

Thanks a lot--

Luke




{quote}""".format(todo = todo, name = name, quote = get_quote()))


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
                          'Adam': 'adamredmer@hotmail.com',
                          'Madison': 'catladiesrun@gmail.com',
                          'Sylvestre': 'sylvesterpineau409@gmail.com',
                          'Rachel' : 'rachel.koeter@gmail.com',
                          'Kathryn': 'kathrynmkaihlanen@utexas.edu',
                          'Ben': 'benwhelan@utexas.edu',
                          'Teja': 'tejasebastian@gmail.com',
                          'Amogh': 'amoghkashyap55@gmail.com',
                          'Jessika': 'jessika.mcfarland@utexas.edu',
                          'Claire': 'claire.mayorga19@gmail.com',
                          'Jeffrey': 'wjalliston@utexas.edu',
                          'Remedy': 'remedyrule9@gmail.com',
                          'Presley': 'presley.mackey@utexas.edu',
                          'Vishaal': 'vishaalsakthi04@utexas.edu',
                          'Sam': 'samantha.kagel@utexas.edu'}

        # create series of lists
        names = []
        emails = []
        racks = []
        shelves = []

        # find out who hasn't been doing their water changes
        regex = re.compile('[^a-zA-Z]')
        for row in rows:
            # if they haven't done their water change, record
            # a bunch of variables stored in lists
            if sheet.cell(row, 5).value.lower() not in acceptable_responses:
                name = sheet.cell(row, 4).value
                # exclude any non-alphabetic symbols from the name
                name = regex.sub('', name)
                if name not in email_addresses.keys():
                    print("no email address for {}!".format(name))
                else:
                    names.append(name)
                    emails.append(email_addresses[name])
                    racks.append(sheet.cell(row, 2).value)
                    shelves.append(sheet.cell(row, 3).value)

        # create dict of those to emails
        to_email = dict((k, email_addresses[k]) for k in names)

        info = {}

        # loop through the new dict
        for name, email in to_email.items():

            # get the racks and shelves for that person
            out = [[racks[i], shelves[i]] for i, nombre in enumerate(names) if nombre == name]

            # make into lists`
            r = []
            s = []

            for x, y in out:
                r.append(x)
                s.append(y)

            info[email] = [[name], r, s]

        # get password stored as environmental variable
        p = os.environ['gmail']

        # send the emails
        try:
            send_email(info, p)
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
