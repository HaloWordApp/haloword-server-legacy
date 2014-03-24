from flask import Flask
from flask_redis import Redis

import requests

app = Flask(__name__)
REDIS_URL = "redis://localhost:6379/0"
redis_store = Redis(app)

API_URL = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}?key=6d9366e8-dc95-4b44-931a-ff90bc8f96bd"


@app.route("/<word>")
def index(word):
    if not redis_store.exists(word):
        text = requests.get(API_URL.format(word)).text
        redis_store.set(word, text)
        return text
    else:
        return redis_store.get(word)


if __name__ == "__main__":
    app.debug = True
    app.run()
