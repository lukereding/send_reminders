# send_reminders

Sends reminders to undergrad, automatically, when they don't do their fish care chores. Reads data from [this](https://docs.google.com/spreadsheets/d/1pVwqyetFLGVl_2qQ40qCH0Nvhe7ODzKC7J_oyQsiOQg/edit#gid=0) Google spreadsheet. Written based on code [here](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) and [here](https://automatetheboringstuff.com/chapter16/). Run like

```bash

 /Users/lukereding/anaconda2/envs/google_sheets/bin/python reminder.py --help

usage: reminder.py [-h] [-e] [-t]

optional arguments:
  -h, --help   show this help message and exit
  -e, --email  Send email to those that have not done water changes?
  -t, --text   Send text message to those that have not done water changes?


```

...using the path to the python interpreter in the virtual environmental called `google_sheets`.

Meant to be executed in as a cron job.
