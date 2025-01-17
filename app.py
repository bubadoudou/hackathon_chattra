# import files
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from wit import Wit
from amadeus import Client, ResponseError

"""Define const paras S"""
DEBUG = 1

G_SEASONS_SWITCHER = {
    1: 'winter',
    1: 'winter',
    1: 'winter',
    2: 'spring',
    2: 'spring',
    2: 'spring',
    3: 'summer',
    3: 'summer',
    3: 'summer',
    4: 'autumn',
    4: 'autumn',
    4: 'autumn'
}

# April to June
SPRING_PLACES = [
    {'name': 'Da Nang - Hoi An', 'nearest_airport': 'DAD', 'visit': 'Ba Na Hills ', 'eat': 'Quan Mi Quang Thi',
     'play': 'go diving in Cu Lao Cham', 'hotel': 'Sala Danang Beach Hotel'},

    {'name': 'Ninh Binh', 'nearest_airport': 'HAN', 'visit': 'Trang An', 'eat': 'Nha Hang Hoang Long',
     'play': 'go to Van Long Wetland Nature Reserve', 'hotel': 'MOMALI Hotel Ninh Binh'},

    {'name': 'Hoa Binh', 'nearest_airport': 'HAN', 'visit': 'Thung Nai', 'eat': 'Nha hang Hoa Qua Son',
     'play': 'go bathing at Cuu thac Tu Son', 'hotel': 'Serena Kim Boi Resort'}
]

# July to September
SUMMER_PLACES = [
    {'name': 'Can Tho', 'nearest_airport': 'VCA', 'visit': 'Cai Rang Floating Market', 'eat': 'Banh Cong Co Ut',
     'play': 'go to My Khanh Tourist Village', 'hotel': 'Vinpearl Hotel Can Tho'},

    {'name': 'Nha Trang', 'nearest_airport': 'CXR', 'visit': 'Hon Mun Island', 'eat': 'Banh Canh Ba Thua',
     'play': 'go to Vinpearl Land Nha Trang', 'hotel': 'Sheraton Nha Trang'},

    {'name': 'Ha Noi', 'nearest_airport': 'HAN', 'visit': 'Ha Noi old streets', 'eat': 'Pho 10 Ly Quoc Su',
     'play': 'go around at Royal City', 'hotel': 'Acoustic Hotel & Spa'}
]

# October to December
FALL_PLACES = [
    {'name': 'Phu Quoc', 'nearest_airport': 'PQC', 'visit': 'Bai Dai', 'eat': 'Xin Chao seafood restaurant',
     'play': 'go to Hon Mong Tay', 'hotel': 'Salinda Resort Phu Quoc Island'},

    {'name': 'Ha Giang', 'nearest_airport': 'HAN', 'visit': 'Dong Van Karst Plateau Geopark',
     'eat': 'Giang Son restaurant', 'play': 'attend Tam Giac Mach flower festival', 'hotel': "Be's Home"},

    {'name': 'Sapa', 'nearest_airport': 'DIN', 'visit': 'Fanxipang', 'eat': 'A Phu restaurant', 'play': 'go trekking',
     'hotel': 'Sapa Horizon Hotel'}
]

# January to March
WINTER_PLACES = [
    {'name': 'Da Lat', 'nearest_airport': 'DLI', 'visit': 'Pongour waterfall', 'eat': 'Dinh Doi Trang restaurant',
     'play': 'go to Valley Of Love', 'hotel': 'Anada Suites Hotel'},

    {'name': 'Ho Chi Minh City', 'nearest_airport': 'SGN', 'visit': 'Ben Thanh market',
     'eat': 'go to Bui Vien western style street', 'play': 'The BCR District 9', 'hotel': 'Sherwood Suites'},

    {'name': 'Moc Chau', 'nearest_airport': 'HAN', 'visit': 'Pine Forest in Ang village',
     'eat': 'Chau Moc Quan restaurant', 'play': 'go to Happy Land', 'hotel': 'The November'}
]

RANDOM_RESPONSES = ["You can try to ask me where you should go on a vacation",
                    "Try something like 'I want to travel from Hanoi to Ho Chi Minh City'",
                    "You can also query flights, just try it"]

GREETING_RESPONSES = ["Hey", "Hey, how're you?", "*Nods* *Nods*", "Hello, how you doing?", "Hello",
                      "Welcome, I am good and you?", "Bonjour!"]

SUGGESTION_RESPONSES = ["Oh yeah, so you want to travel in {} huh? How about planning a trip to {}",
                        "Wanna chill out {}? Let's travel to {}"]

ACCOMMODATION_RESPONSES = ["I suggest you to book a room at {}"]

ATTRACTION_RESPONSES = ["I would recommend you to visit {}"]

ACTIVITY_RESPONSES = ["You can {}"]

RESTAURANT_RESPONSES = ["You should try some dishes from {}"]

I_LOCATION = "location_suggest"  # $wit/location_suggest
I_FLIGHT = "flight_inquiry"
I_ACCOMMODATION = "accommodation_suggest"
I_ACTIVITY = "activity_suggest"
I_RESTAURANT = "restaurant_suggest"

"""Define const paras E"""

g_travel_season = ""
g_travel_date = ""
g_depart_city = ""
g_des_city = ""
g_suggest_des_city = {}

# app name
app = Flask("Chattra")

# Wit.ai API
access_token = "QYM5JWAO6JGZZIXQMYNJDNX74PM4C5IJ"
client = Wit(access_token)

# Amadeus flight API
g_amadeus = Client(client_id="O14yETMZyjDB7AgA1VWGmGPzAiWn8P3a", client_secret="iyO7N5thzfGu5m6F")


def is_season(input_str):
    # if user input not a travel season, then determin user only want to book a flight on a specific date.
    # else return travel season
    ret_val = input_str['entities'].get('wit$datetime:datetime')[0].get('type')
    if ret_val == 'interval':
        return True
    else:
        return False


def cvt_datetime2season(input_str):
    ret_val = ""

    _date = input_str['entities']['wit$datetime:datetime'][0]['value']
    _date = _date[:10]

    _date_obj = datetime.strptime(_date, '%Y-%m-%d').date()

    season_idx = (_date_obj.month % 12 + 3) // 3

    ret_val = G_SEASONS_SWITCHER.get(season_idx)

    return ret_val


def get_travel_season(input_str):
    ret_val = ""
    if is_season(input_str):
        ret_val = input_str['entities'].get('wit$datetime:datetime')[0].get('body')
    else:
        ret_val = cvt_datetime2season(input_str)

    return ret_val


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


def get_random_response():
    return str(random.choice(RANDOM_RESPONSES))

def get_greeting_response():
    return str(random.choice(GREETING_RESPONSES))


def get_destination(travel_season):
    suggest_des_city = {}
    if 'winter' in travel_season:
        suggest_des_city = random.choice(WINTER_PLACES)
    elif 'spring' in travel_season:
        suggest_des_city = random.choice(SPRING_PLACES)
    elif 'summer' in travel_season:
        suggest_des_city = random.choice(SUMMER_PLACES)
    elif 'autumn' or 'fall' in travel_season:
        suggest_des_city = random.choice(FALL_PLACES)

    return suggest_des_city


# if intent = location_suggest
def handle_loc_suggest(usr_resp):
    ret_val = ""
    global g_travel_season
    global g_suggest_des_city
    g_travel_season = get_travel_season(usr_resp)

    if not g_suggest_des_city:
        g_suggest_des_city = get_destination(g_travel_season)
        ret_val = str(random.choice(SUGGESTION_RESPONSES)).format(g_travel_season, g_suggest_des_city['name'])

    return ret_val


def handle_accom_suggest(usr_resp):
    ret_val = str(random.choice(ACCOMMODATION_RESPONSES)).format(g_suggest_des_city['hotel'])
    return ret_val


def handle_act_suggest(usr_resp):
    if usr_resp['entities'].get('activity_type:play'):
        ret_val = str(random.choice(ACTIVITY_RESPONSES)).format(g_suggest_des_city['play'])
    elif usr_resp['entities'].get('activity_type:visit'):
        ret_val = str(random.choice(ATTRACTION_RESPONSES)).format(g_suggest_des_city['visit'])
    else:
        ret_val = "Sorry malfunctioned"
    return ret_val


def handle_res_suggest(usr_resp):
    ret_val = str(random.choice(ACCOMMODATION_RESPONSES)).format(g_suggest_des_city['eat'])
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
        msg1 = get_greeting_response()
        msg2 = get_random_response()
        ret_val = jsonify(msg1, msg2)
    elif l_trait == "wit$bye":
        ret_val = "See ya later"
    else:
        print(str(resp))
        l_intent = get_intent(resp)
        print(l_intent)
        if l_intent == I_LOCATION:
            ret_val = handle_loc_suggest(resp)
        elif l_intent == I_ACCOMMODATION:
            ret_val = handle_accom_suggest(resp)
        elif l_intent == I_ACTIVITY:
            ret_val = handle_act_suggest(resp)
        elif l_intent == I_RESTAURANT:
            ret_val = handle_res_suggest(resp)
        else:
            ret_val = get_random_response()
    return ret_val


if __name__ == "__main__":
    app.run(debug=True)
