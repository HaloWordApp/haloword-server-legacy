from flask import Flask, Response
import redis
import requests
import urllib
from settings import API_KEY

app = Flask(__name__)
redis_store = redis.StrictRedis(host='localhost', port=6233, db=0)

API_URL = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}"


@app.route("/webster/query/<word>")
def index(word):
    word = word.lower().strip()
    text = ""

    if not redis_store.exists(word):
        word_urlencoded = urllib.quote_plus(word.encode("utf8"))
        if len(word) < 40:
            text = requests.get(API_URL.format(word_urlencoded), params={"key": API_KEY}).text
            redis_store.set(word, text)
    else:
        text = redis_store.get(word)

    redis_store.incr(word + ":count")

    headers = {"Cache-Control": "max-age=%d" % (3600 * 24 * 7,)}
    return Response(response=text,
                    status=200,
                    mimetype="application/xml",
                    headers=headers)


@app.route("/webster/list/")
def word_list():
    keys = sorted(redis_store.keys())
    html = "<pre>" + "\n".join(keys)
    html += "\n\nTotal: {}".format(len(keys)) + "</pre>"
    return html


@app.route("/webster/count/")
def request_count():
    keys = redis_store.keys(pattern="*:count")
    results = [{"key": key[:-6], "value": redis_store.get(key)} for key in keys]
    results = sorted(results, key=lambda r: int(r["value"]), reverse=True)

    formated_results = ["{:>8}  {}".format(result["value"], result["key"]) for result in results]
    html = "<pre>" + "\n".join(formated_results)
    html += "\n\nTotal: {}".format(len(keys)) + "</pre>"

    return html


if __name__ == "__main__":
    app.debug = True
    app.run()
