from flask import Flask, Response
import redis
import requests
import urllib
from settings import API_KEYS, YOUDAO_API_KEYFROM, YOUDAO_API_KEY

app = Flask(__name__)
redis_host = "localhost" if __name__ == "__main__" else "redis"
redis_store_webster = redis.StrictRedis(host=redis_host, port=6379, db=0)
redis_store_youdao = redis.StrictRedis(host=redis_host, port=6379, db=1)

API_URL = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{}"


@app.route("/youdao/query/<word>")
def youdao(word):
    if not redis_store_youdao.exists(word):
        url = "https://fanyi.youdao.com/fanyiapi.do?keyfrom={}&key={}&type=data&doctype=json&version=1.1&q={}".format(
            YOUDAO_API_KEYFROM,
            YOUDAO_API_KEY,
            urllib.quote_plus(word.encode("utf8"))
        )

        response = requests.get(url)
        result = response.text

        try:
            response.json()
        except ValueError:
            pass
        else:
            redis_store_youdao.set(word, result)
    else:
        result = redis_store_youdao.get(word)

    redis_store_youdao.incr(word + ":count")

    headers = {"Cache-Control": "max-age=%d" % (3600 * 24 * 7,)}
    return Response(response=result,
                    status=200,
                    mimetype="application/json",
                    headers=headers)


@app.route("/webster/query/<word>")
def webster(word):
    word = word.lower().strip()

    if not redis_store_webster.exists(word):
        word_urlencoded = urllib.quote_plus(word.encode("utf8"))
        if len(word) < 40:
            API_KEY = API_KEYS[len(word) % len(API_KEYS)]  # alternate between API keys
            result = requests.get(API_URL.format(word_urlencoded), params={"key": API_KEY}).text
            redis_store_webster.set(word, result)
    else:
        result = redis_store_webster.get(word)

    redis_store_webster.incr(word + ":count")

    headers = {"Cache-Control": "max-age=%d" % (3600 * 24 * 7,)}
    return Response(response=result,
                    status=200,
                    mimetype="application/xml",
                    headers=headers)


@app.route("/webster/list/")
def word_list():
    keys = sorted(redis_store_webster.keys())
    html = "<pre>" + "\n".join(keys)
    html += "\n\nTotal: {}".format(len(keys)) + "</pre>"
    return html


@app.route("/webster/count/")
def request_count():
    keys = redis_store_webster.keys(pattern="*:count")
    results = [{"key": key[:-6], "value": redis_store_webster.get(key)} for key in keys]
    results = sorted(results, key=lambda r: int(r["value"]), reverse=True)

    formated_results = ["{:>8}  {}".format(result["value"], result["key"]) for result in results]
    html = "<pre>" + "\n".join(formated_results)
    html += "\n\nTotal: {}".format(len(keys)) + "</pre>"

    return html


if __name__ == "__main__":
    app.debug = True
    app.run()
