# import files
from flask import Flask, render_template, request
from wit import Wit

# app name
app = Flask("Chattra")

# Wit.ai API
access_token = "QYM5JWAO6JGZZIXQMYNJDNX74PM4C5IJ"
client = Wit(access_token)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    resp = client.message(user_text)
    return str(resp)


if __name__ == "__main__":
    app.run()
