# import files
import random
from flask import Flask, render_template, request
from wit import Wit

"""Define const paras S"""
GREETING_RESPONSES = ["Hey", "Hey, how're you?", "*Nods* *Nods*", "Hello, how you doing?", "Hello",
                      "Welcome, I am good and you?", "Bonjour!"]

DEBUG = 1
"""Define const paras E"""


# app name
app = Flask("Chattra")

# Wit.ai API
access_token = "QYM5JWAO6JGZZIXQMYNJDNX74PM4C5IJ"
client = Wit(access_token)


def get_intent(input_str):
    """
    Get intent from wit response
    :param input_str: wit.ai response
    :return: intent in string
    """


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

@app.route("/")
def index():
    return render_template("homepage.html")


@app.route("/chattra")
def chattra():
    return render_template("chatbox.html")

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
    app.run()
