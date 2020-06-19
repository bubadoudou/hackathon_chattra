# import files
import random
from flask import Flask, render_template, request
from wit import Wit
from amadeus import Client, ResponseError

"""Define const paras S"""
DEBUG = 1

GREETING_RESPONSES = ["Hey", "Hey, how're you?", "*Nods* *Nods*", "Hello, how you doing?", "Hello",
                      "Welcome, I am good and you?", "Bonjour!"]

SUGGESTION_RESPONSES = ["Oh yeah, so you want to travel in {} huh? Let's me think for a while \n tik tok tik tok", 
                        "Wanna chill out {}? Hold on a second, my brain is procesisng..."]

I_LOC = "location_suggest" # $wit/location_suggest
I_FLI = "flight_inquiry"

"""Define const paras E"""

g_travel_season = ""

# app name
app = Flask("Chattra")

# Wit.ai API
access_token = "QYM5JWAO6JGZZIXQMYNJDNX74PM4C5IJ"
client = Wit(access_token)

# Amadeus flight API
g_amadeus = Client(client_id = "O14yETMZyjDB7AgA1VWGmGPzAiWn8P3a", client_secret = "iyO7N5thzfGu5m6F")


def get_travel_season(input):
    return input['entities']['wit$datetime:datetime'][0]['body']


def get_intent(input_str):
    """
    Get intent from wit response
    :param input_str: wit.ai response
    :return: intent in string
    """
    intent = ""

    if not input_str.get('intents'):
        return ""
    else:
        intent = list(input_str['intents'].keys())[1]

    if intent == I_LOC:
        g_travel_season = get_travel_season(input_str)
        return intent
    elif intent == I_FLI:
        return intent


def get_trait(input_str):
    """
    Get trait (if any) from wit response
    :param input_str:
    :return:
    """
    if not input_str.get('traits'):
        return {}
    else:
        return list(input_str['traits'].keys())[0]



def get_greeting_response():
    return str(random.choice(GREETING_RESPONSES))


def get_suggestion_response():
    return str(random.choice(SUGGESTION_RESPONSES)).format(g_travel_season)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    ret_val = ""
    user_text = request.args.get('msg')
    resp = client.message(user_text)



    if not get_trait(resp):
        ret_val = str(resp)
    else:
        _trait = str(get_trait(resp))
        if DEBUG:
            print(_trait)
        if _trait == "wit$greetings":
            ret_val = get_greeting_response()

    return ret_val


if __name__ == "__main__":
    app.run(debug = True)
