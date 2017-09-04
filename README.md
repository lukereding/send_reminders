# send_reminders

Sends reminders to undergrads, automatically, when they don't do their fish care chores. 

Reads data from [this](https://docs.google.com/spreadsheets/d/1pVwqyetFLGVl_2qQ40qCH0Nvhe7ODzKC7J_oyQsiOQg/edit#gid=0) Google spreadsheet. Written based on code [here](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) and [here](https://automatetheboringstuff.com/chapter16/). 

Run like

```bash

 /Users/lukereding/anaconda2/envs/google_sheets/bin/python reminder_water_change.py --help

usage: reminder_water_change.py [-h] [-e] [-t]

optional arguments:
  -h, --help   show this help message and exit
  -e, --email  Send email to those that have not done water changes?
  -t, --text   Send text message to those that have not done water changes?


```

...using the path to the python interpreter in the virtual environmental called `google_sheets`. This is recommended but not necessary.

Its meant to be executed in as a cron job.

`reminder_water_change.py` finds the previous Monday's date. It's meant to be executed on Thursday and Friday. So in `crontab -e`, add

> 26 4 * * 4 . $HOME/.profile && /home/pi/miniconda3/envs/send_emails/bin/python /home/pi/Documents/send_reminders/reminder_water_change.py -e
> 26 4 * * 5 . $HOME/.profile && /home/pi/miniconda3/envs/send_emails/bin/python /home/pi/Documents/send_reminders/reminder_water_change.py -e
> 26 4 * * 1 . $HOME/.profile && /home/pi/miniconda3/envs/send_emails/bin/python /home/pi/Documents/send_reminders/reminder_water_change.py -e

to check the google sheet and send an email every Monday, Thursday, and Friday at 4:26am. 
