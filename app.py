#!/usr/bin/env python3

import re
import random
from datetime import datetime
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from messages.twilio_messaging_api import TwilioMessagingAPI

from utils.date_utils import get_day_of_week
from utils.json_utils import load_json_file
from utils.ngrok import Ngrok
from utils.socket_utils import IP

from tinydb import TinyDB, Query

# INIT FLASK APP
app = Flask(__name__)

# init ngrok tunnel to messaging service
app.ng = Ngrok()
app.ng.init()
app.webhook = f"{app.ng.public_url}/sms"
app.messaging_api = TwilioMessagingAPI(app.webhook)
print(f"HTTP tunnel via Ngrok at: {app.webhook}")

"""
------------------------------------------
---------------- DATABASE ----------------
------------------------------------------
"""

# see if there is an existing DB for all the cockails
app.cuisines_db = TinyDB('./database/cuisines_db.json')
app.drinks_db = TinyDB('./database/drinks_db.json')
app.restaurants_db = TinyDB('./database/restaurants_db.json')
app.choices = {}

def send_weekly_report():
    people = ["kris", "john"]
    app.choices = {
        "monday": {"cuisine": None, "cocktail": None, "chef": None, "barista": None},
        "tuesday": {"cuisine": None, "cocktail": None, "chef": None, "barista": None},
        "wednesday": {"cuisine": None, "cocktail": None, "barista": None},
        "thursday": {"cuisine": None, "cocktail": None, "chef": None, "barista": None},
        "friday": {"cuisine": None, "cocktail": None, "chef": None, "barista": None},
        "saturday": {"cuisine": None, "cocktail": None, "chef": None, "barista": None},
        "sunday": {"cocktail": None, "barista": None}
    }

    # remove the day we aren't doing anything on
    days = ["monday", "tuesday", "thursday", "friday", "saturday"]
    order_in_day = random.choice(days)
    try:
        days.remove(order_in_day)
    except ValueError:
        pass
    app.choices[order_in_day] = {"cocktail": None, "barista": None}

    # pick random baristas for the days you're not cooking
    app.choices[order_in_day]["barista"] = random.choice(people)
    app.choices["sunday"]["barista"] = random.choice(people)
    app.choices["wednesday"]["barista"] = random.choice(people)

    # ----------------------------------------
    # --------------- CUISINES ---------------
    # ----------------------------------------

    # get largest number of times you've eaten any cuisine
    cuisines = app.cuisines_db.all()
    max_times_cooked = max(map(lambda x: x["times_cooked"], cuisines))
    max_times_restaurant = max(map(lambda x: x["times_restaurant"], cuisines))

    # init lists for binning our app.choices
    cooked_choices = []
    cooked_rest = []

    restaurant_choices = []
    restaurant_rest = []

    # make the bins
    for cuisine in cuisines:
        if cuisine["times_cooked"] < max_times_cooked:
            cooked_choices.append(cuisine)
        else:
            cooked_rest.append(cuisine)
        
        if cuisine["times_restaurant"] < max_times_restaurant:
            restaurant_choices.append(cuisine)
        else:
            restaurant_rest.append(cuisine)
    
    # pool of people to choose from
    chefs = people * 2

    for day in days:
        if len(cooked_choices) == 0:
            cooked_choices = cooked_rest

        # pick the cuisine to cook
        cuisine_to_cook = random.choice(cooked_choices)
        app.choices[day]["cuisine"] = cuisine_to_cook

        # pick the person to cook
        chef = random.choice(chefs)
        app.choices[day]["chef"] = chef
        try:
            chefs.remove(chef)
        except ValueError:
            pass

        # choose a barista that isn't the chef
        app.choices[day]["barista"] = "kris" if chef == "john" else "john"

        # remove this choice from the cooking pool
        try:
            cooked_choices.remove(cuisine_to_cook)
        except ValueError:
            pass
        
        # update the DB
        app.cuisines_db.update(
            {"times_cooked": cuisine_to_cook["times_cooked"] + 1},
            Query().type == cuisine_to_cook['type']
        )

        # remove this choice from the restaurant cuisine pool
        # make sure there's at least one restaurant choice left
        if (len(restaurant_choices) > 1):
            try:
                restaurant_choices.remove(cuisine_to_cook)
            except ValueError:
                pass
        if (len(restaurant_rest) > 1):
            try:
                restaurant_rest.remove(cuisine_to_cook)
            except ValueError:
                pass

    # if all restaurants have been seen the max num of times,
    # just pick from all restaurants
    if len(restaurant_choices) == 0:
        restaurant_choices = restaurant_rest
    restaurant_cuisine = random.choice(restaurant_choices)
    app.choices["wednesday"]["cuisine"] = restaurant_cuisine
    app.cuisines_db.update(
        {"times_restaurant": restaurant_cuisine["times_restaurant"] + 1},
        Query().type == restaurant_cuisine['type']
    )
    
    # -----------------------------------------
    # --------------- COCKTAILS ---------------
    # -----------------------------------------
    # get largest number of times you've eaten any cuisine
    cocktails = app.drinks_db.all()
    cocktail_choices = []

    for cocktail in cocktails:
        if cocktail.get("times_used") == 0:
            cocktail_choices.append(cocktail)

    for day in app.choices.keys():
        cocktail_chosen = random.choice(cocktail_choices)
        app.choices[day]["cocktail"] = cocktail_chosen
        try:
            cocktail_choices.remove(cocktail_chosen)
        except ValueError:
            pass
        app.drinks_db.update(
            {"times_used": cocktail_chosen["times_used"] + 1},
            Query().name == cocktail_chosen['name']
        )

    # --------------------------------------
    # --------------- REPORT ---------------
    # --------------------------------------
    report = []
    for day in app.choices.keys():
        report.append(f"{make_choice_string(day)}")

    # send out the report
    send_message_to_bois("\n\n".join(report))

def make_choice_string(day):
        string = f"{day}: "

        if app.choices[day].get("cuisine"):
            if day == "wednesday":
                string += f"y'all are eating out at a {app.choices[day]['cuisine']['type']} restaurant"
            else:
                string += f"{app.choices[day]['chef']} is cooking {app.choices[day]['cuisine']['type']}"
        else:
            string += "no meal planned"

        if app.choices[day].get("cocktail"):
            string += f", {app.choices[day]['barista']} is making the {app.choices[day]['cocktail']['name']} (#{app.choices[day]['cocktail']['index']}) cocktail"

        return string

def get_day():
    return get_day_of_week(datetime.now()).lower()

def send_reminder():
    send_message_to_bois("reminder - " + make_choice_string(get_day()))

def send_review_reminder():
    send_message_to_bois(f"don't forget to review today's cocktail, {app.choices[get_day()]['cocktail']['name']}")

def send_message_to_bois(message):
    # load people to send to
    bois = load_json_file("bois.json")

    # send out the texts
    for boi in bois:
        app.messaging_api.send_message(message, boi)

"""
-------------------------------------------
---------------- SCHEDULER ----------------
-------------------------------------------
"""
# initialize scheduler
app.bg_scheduler = BackgroundScheduler(daemon=True)

# DEFINE RECURING JOBS FOR THE SCHEDULER

# send the weekly overview on sunday at 8AM
send_weekly_report() # initial report
app.bg_scheduler.add_job(send_weekly_report, 'cron', day_of_week='sun', hour=8, minute=0)

# each day, remind what the recipe and cocktail for that day is
app.bg_scheduler.add_job(send_reminder, 'cron', day_of_week='mon-sun', hour=7, minute=30)

# each day, remind the user to review the cocktail
app.bg_scheduler.add_job(send_review_reminder, 'cron', day_of_week='mon-sun', hour=17, minute=25)

# start scheduler
app.bg_scheduler.start()

def review_cocktail(user, score, review):
    cocktail_obj = app.choices[get_day()]['cocktail']
    reviews = cocktail_obj['reviews']
    reviews.append({
        "from": user,
        "score": score,
        "review": review,
        "timestamp": gen_timestamp()
    })
    app.drinks_db.update(
        {"reviews": reviews},
        Query().name == cocktail_obj['name']
    )

    return f"recorded your review of today's cocktail, {cocktail_obj['name']}!"

def review_restaurant(user, name, score, review):
    this_weeks_restaurant = None
    this_weeks_restaurant_list = app.restaurants_db.search(Query().name == name)
    if len(this_weeks_restaurant_list) > 0:
        this_weeks_restaurant = this_weeks_restaurant_list[0]
    
    if this_weeks_restaurant:
        existing_reviews = this_weeks_restaurant['reviews']
        existing_reviews.append({
            "from": user,
            "score": score,
            "review": review,
            "timestamp": gen_timestamp()
        })

        app.restaurants_db.update(
            {"reviews": existing_reviews},
            Query().name == name
        )
    else:
        reviews = []
        reviews.append({
            "from": user,
            "score": score,
            "review": review,
            "timestamp": gen_timestamp()
        })

        app.restaurants_db.insert(
            {"reviews": reviews, "name": name}
        )

    return f"recorded your review of the restaurant, {name}!"

timestamp_format = "%Y-%m-%d %H:%M:%S"
new_york_timezone = pytz.timezone('America/New_York') 
def gen_timestamp():
    datetime_NY = datetime.now(new_york_timezone)
    return datetime_NY.strftime(timestamp_format)

def handle_response(content, user):
    if content.startswith("COCKTAIL\n"):
        try:
            score = re.search("score:[\s]*(.*)(\n|$)", content).groups()[0]
        except AttributeError:
            return "i need a score"

        try:
            review = re.search("review:[\s]*(.*)(\n|$)", content).groups()[0]
        except AttributeError:
            return "i need a review"

        return review_cocktail(user, score, review)
    elif content.startswith("RESTAURANT\n"):
        try:
            name = re.search("name:[\s]*(.*)(\n|$)", content).groups()[0]
            name = name.lower()
        except AttributeError:
            return "i need a name"

        try:
            score = re.search("score:[\s]*(.*)(\n|$)", content).groups()[0]
        except AttributeError:
            return "i need a score"

        try:
            review = re.search("review:[\s]*(.*)(\n|$)", content).groups()[0]
        except AttributeError:
            return "i need a review"
    
        return review_restaurant(user, name, score, review)
    else:
        return f"sorry {user}, i don't understand lol drill go brrrr"

""" THIS IS OUR HANDLER FOR INCOMING MESSAGES """
@app.route(f"/sms", methods=["POST"])
def sms_reply():
    # get content of recieved text message
    content = request.values.get("Body", "")
    user = None

    for boi in load_json_file("bois.json"):
        if boi["phone_number"] == request.values.get("From", ""):
            user = boi["first_name"].lower()

    # handle the response
    response_object = MessagingResponse()
    try:
        response_message = handle_response(content, user)
    except Exception as e:
        response_message = str(e)

    # send back to the person that sent it!
    response_object.message(response_message)
    return str(response_object)

if __name__ == "__main__":
    app.run(debug=False, threaded=True)
