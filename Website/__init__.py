from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["Secret_Key"] = "my_secret_key"
    return app
