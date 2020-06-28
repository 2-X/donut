#!/usr/bin/env python3

import random
import datetime
import re

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from messages.twilio_messaging_api import TwilioMessagingAPI

from utils.ngrok import Ngrok
from utils.socket_utils import IP

# INIT FLASK APP
app = Flask(__name__)

# init ngrok tunnel to messaging service
app.ng = Ngrok()
app.ng.init()
app.webhook = f"{app.ng.public_url}/sms"
app.messaging_api = TwilioMessagingAPI(app.webhook)
print(f"HTTP tunnel via Ngrok at: {app.webhook}")


"""
-------------------------------------------
---------------- SCHEDULER ----------------
-------------------------------------------
"""
# initialize scheduler
app.bg_scheduler = BackgroundScheduler(daemon=True)

# DEFINE RECURING JOBS FOR THE SCHEDULER

# send the weekly overview on sunday at 8AM
# app.bg_scheduler.add_job(send_num_new_users_text, 'cron', day_of_week='sun', hour=8, minute=0)

# each day, remind what the recipe and cocktail for that day is
# app.bg_scheduler.add_job(approve_requests_and_update_number, 'interval', minutes=120)

# start scheduler
app.bg_scheduler.start()

def handle_response(content):
    if content == "hi":
        return "hey what's up"
    else:
        return "i don't understand lol drill go brrrr"

""" THIS IS OUR HANDLER FOR INCOMING MESSAGES """
@app.route(f"/sms", methods=["POST"])
def sms_reply():
    # get content of recieved text message
    content = request.values.get("Body", "")

    # handle the response
    response_object = MessagingResponse()
    try:
        response_message = handle_response(content)
    except Exception as e:
        response_message = str(e)

    # send back to the person that sent it!
    response_object.message(response_message)
    return str(response_object)

if __name__ == "__main__":
    app.run(debug=False, threaded=True)
