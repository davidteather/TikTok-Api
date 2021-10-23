import random
from TikTokApi import browser
from TikTokApi import TikTokApi
from flask import Flask, request, jsonify
from gevent import monkey

monkey.patch_all()


proxy = None

signing_browser = browser.browser(proxy=proxy)

app = Flask(__name__)


@app.route("/sign", methods=["GET"])
def sign_url():
    url = request.args.get("url")
    device_id = request.args.get("custom_device_id", None)
    if url is None:
        return jsonify({"success": False, "error": "You must provide a URL"})

    if device_id is not None:
        device_id = str(random.randint(10000, 999999999))
    verifyFp, device_id, _signature = signing_browser.sign_url(
        url=url, custom_device_id=device_id
    )

    return jsonify(
        {
            "verifyFp": verifyFp,
            "device_id": device_id,
            "_signature": _signature,
            "userAgent": signing_browser.userAgent,
            "referrer": signing_browser.referrer,
        }
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
    print("Cleaning Up")
    try:
        signing_browser.clean_up()
    except Exception:
        pass
    try:
        browser.get_playwright().stop()
    except Exception:
        pass

# Example script below for production use

# from TikTokApi import TikTokApi
# api = TikTokApi(external_signer="http://localhost:5000/sign")
# print(api.trending())
