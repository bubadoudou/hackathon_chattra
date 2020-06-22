# import files
import random
from flask import Flask, render_template, request
from wit import Wit
from amadeus import Client, ResponseError

"""Define const paras S"""
DEBUG = 1

# April to June
SPRING_PLACES = ['Da Nang - Hoi An', 'Ninh Binh', 'Hoa Binh']

# July to September
SUMMER_PLACES = ['Can Tho', 'Nha Trang', 'Ha Noi']

# October to December
FALL_PLACES = ['Phu Quoc', 'Ha Giang', 'Sapa']

# January to March
WINTER_PLACES = ['Da Lat', 'Ho Chi Minh City', 'Moc Chau']

GREETING_RESPONSES = ["Hey", "Hey, how're you?", "*Nods* *Nods*", "Hello, how you doing?", "Hello",
                      "Welcome, I am good and you?", "Bonjour!"]

SUGGESTION_RESPONSES = ["Oh yeah, so you want to travel in {} huh? How about plan a trip to {}",
                        "Wanna chill out {}? Let's travel to {}"]

I_LOC = "location_suggest"  # $wit/location_suggest
I_FLI = "flight_inquiry"
I_ACCOM = "accommodation_suggest"
I_ACT = "activity_suggest"

"""Define const paras E"""

g_travel_season = ""
g_depart_city = ""
g_des_city = ""

# app name
app = Flask("Chattra")

# Wit.ai API
access_token = "QYM5JWAO6JGZZIXQMYNJDNX74PM4C5IJ"
client = Wit(access_token)

# Amadeus flight API
g_amadeus = Client(client_id="O14yETMZyjDB7AgA1VWGmGPzAiWn8P3a", client_secret="iyO7N5thzfGu5m6F")


def get_travel_season(input_str):
    return input_str['entities'].get('wit$datetime:datetime')[0].get('body')


def get_intent(usr_resp):
    """
    Get intent from wit response
    :param usr_resp: wit.ai response
    :return: intent in string
    """
    if not usr_resp.get('intents'):
        return ""
    else:
        intent = usr_resp['intents'][0].get('name')
        return intent


def get_trait(usr_resp):
    """
    Get trait (if any) from wit response
    :param usr_resp: user response
    :return:
    """
    if not usr_resp.get('traits'):
        return ""
    else:
        return list(usr_resp['traits'].keys())[0]


def get_greeting_response():
    return str(random.choice(GREETING_RESPONSES))


def get_destination(travel_season):
    des_city = ""
    if 'winter' in travel_season:
        des_city = random.choice(WINTER_PLACES)
    elif 'spring' in travel_season:
        des_city = random.choice(SPRING_PLACES)
    elif 'summer' in travel_season:
        des_city = random.choice(SUMMER_PLACES)
    elif 'autumn' or 'fall' in travel_season:
        des_city = random.choice(FALL_PLACES)

    return des_city


# if intent = location_suggest
def handle_loc_suggest(usr_resp):
    ret_val = ""
    global g_travel_season
    global g_des_city
    g_travel_season = get_travel_season(usr_resp)

    if not g_des_city:
        g_des_city = get_destination(g_travel_season)
        ret_val = str(random.choice(SUGGESTION_RESPONSES)).format(g_travel_season, g_des_city)

    return ret_val


def handle_accom(usr_resp):
    ret_val = ""
    return ret_val


def handle_act(usr_resp):
    ret_val = ""
    return ret_val


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    ret_val = ""
    user_text = request.args.get('msg')
    resp = client.message(user_text)

    # Check if the user greets
    l_trait = str(get_trait(resp))
    if l_trait == "wit$greetings":
        ret_val = get_greeting_response()
    else:
        print(str(resp))
        l_intent = get_intent(resp)
        print(l_intent)
        if l_intent == I_LOC:
            ret_val = handle_loc_suggest(resp)
        else:
            ret_val = str(resp)

    return ret_val


if __name__ == "__main__":
    app.run(debug=True)
