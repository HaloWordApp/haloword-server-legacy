from flask import Flask
import redis

import requests

app = Flask(__name__)
redis_store = redis.StrictRedis(host='localhost', port=6233, db=0)

API_URL = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}?key=6d9366e8-dc95-4b44-931a-ff90bc8f96bd"


@app.route("/webster/query/<word>")
def index(word):
    if not redis_store.exists(word):
        print "Not cached:", word
        text = requests.get(API_URL.format(word)).text
        redis_store.set(word, text)
        return text
    else:
        return redis_store.get(word)


if __name__ == "__main__":
    app.debug = True
    app.run()
